"""
HAHA Vending Machine API Integration Module

Real integration with the HAHA Vending API at https://thorapi.hahabianli.com

Authentication:
  POST /open/auth/gettoken  { appkey, appsecret }  -> access_token (valid 15 days)
  All subsequent requests: header  Authorization: <token>  (NO "Bearer" prefix)

Key endpoints used:
  GET /open/order?limit=N&page=N  -> paginated order list
  GET /open/order/{order_no}      -> single order detail

Order status codes:
  100 = Unpaid
  101 = Paid  (the only status counted as revenue)
  102 = No consumption
  103 = Partially paid
  200 = Payment confirmation in progress
"""

import requests
import json
import os
import time
import hmac
import hashlib
import random
import string
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from functools import wraps

logger = logging.getLogger(__name__)


class HAHAVendingAPI:
    """
    Real HAHA Vending Machine API Client.

    Handles token acquisition/caching, order fetching, and revenue aggregation.
    All methods return empty lists / dicts on failure so callers never crash.
    """

    BASE_URL = "https://thorapi.hahabianli.com"

    def __init__(self,
                 appkey: str,
                 appsecret: str,
                 base_url: Optional[str] = None):
        self.appkey = appkey
        self.appsecret = appsecret
        self.base_url = (base_url or self.BASE_URL).rstrip("/")

        # Token cache
        self._token: Optional[str] = None
        self._token_expire: float = 0.0   # Unix timestamp

        # Simple in-memory response cache
        self._cache: Dict[str, Tuple[float, object]] = {}
        self.cache_ttl = 300  # 5 minutes

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Snaxology-Portal/2.0"
        })

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    def _acquire_token(self) -> Optional[str]:
        """Fetch a fresh access token from the HAHA auth endpoint."""
        url = f"{self.base_url}/open/auth/gettoken"
        try:
            resp = self.session.post(
                url,
                json={"appkey": self.appkey, "appsecret": self.appsecret},
                timeout=15
            )
            resp.raise_for_status()
            body = resp.json()
            if body.get("success") == "true" and body.get("data"):
                token = body["data"]["access_token"]
                expire = body["data"].get("expire", 0)
                # Refresh 2 days before actual expiry
                self._token = token
                self._token_expire = float(expire) - 172800
                logger.info("HAHA API: token acquired, expires %s",
                            datetime.fromtimestamp(float(expire)).isoformat())
                return token
            logger.error("HAHA API: token acquisition failed: %s", body)
            return None
        except Exception as exc:
            logger.error("HAHA API: token request exception: %s", exc)
            return None

    def _get_token(self) -> Optional[str]:
        """Return a valid token, refreshing if needed."""
        if self._token and time.time() < self._token_expire:
            return self._token
        return self._acquire_token()

    # ------------------------------------------------------------------
    # Signature generation
    # ------------------------------------------------------------------

    def _generate_signature(self, params: Dict, header_params: Dict) -> str:
        """
        Generate HMAC-SHA256 signature.
        Merges request params + header params (nonce, timestamp, appkey),
        sorts alphabetically, builds query string, signs with appsecret.
        """
        all_params = {}
        for k, v in {**params, **header_params}.items():
            all_params[k] = str(v).strip() if isinstance(v, str) else str(v)
        sorted_items = sorted(all_params.items())
        query_string = "&".join(f"{k}={v}" for k, v in sorted_items)
        sig = hmac.new(
            self.appsecret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return sig

    def _build_signed_headers(self, params: Dict) -> Dict:
        """Build the Authorization + signature headers for a signed request."""
        token = self._get_token()
        if not token:
            return {}
        nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        timestamp = str(int(time.time()))
        header_params = {
            "nonce": nonce,
            "timestamp": timestamp,
            "appkey": self.appkey,
        }
        signature = self._generate_signature(params, header_params)
        return {
            "Authorization": token,
            "nonce": nonce,
            "timestamp": timestamp,
            "signature": signature,
            "appkey": self.appkey,
        }

    # ------------------------------------------------------------------
    # Low-level request helper
    # ------------------------------------------------------------------

    def _get(self, path: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Perform an authenticated GET request with HMAC-SHA256 signature.
        Returns the parsed JSON body, or None on failure.
        """
        if params is None:
            params = {}

        headers = self._build_signed_headers(params)
        if not headers:
            logger.error("HAHA API: no valid token available")
            return None

        url = f"{self.base_url}{path}"
        try:
            resp = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=20
            )
            resp.raise_for_status()
            body = resp.json()
            if body.get("success") == "true":
                return body
            logger.warning("HAHA API: non-success response for %s: code=%s msg=%s",
                           path, body.get("code"), body.get("message"))
            return None
        except requests.exceptions.Timeout:
            logger.error("HAHA API: timeout on %s", path)
        except requests.exceptions.ConnectionError as exc:
            logger.error("HAHA API: connection error on %s: %s", path, exc)
        except requests.exceptions.HTTPError as exc:
            logger.error("HAHA API: HTTP error on %s: %s", path, exc)
        except Exception as exc:
            logger.error("HAHA API: unexpected error on %s: %s", path, exc)
        return None

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def _cache_get(self, key: str) -> Optional[object]:
        if key in self._cache:
            ts, val = self._cache[key]
            if time.time() - ts < self.cache_ttl:
                return val
        return None

    def _cache_set(self, key: str, val: object) -> None:
        self._cache[key] = (time.time(), val)

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def authenticate(self) -> bool:
        """Return True if we can obtain a valid token."""
        return self._get_token() is not None

    def get_orders(self,
                   page: int = 1,
                   limit: int = 100,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   sticker_num: Optional[str] = None,
                   pay_start_time: Optional[str] = None,
                   pay_end_time: Optional[str] = None) -> Dict:
        """
        Fetch a page of orders.

        Returns the full data dict:
          { count, pageCount, pageNow, pageIndex, pageSize, list: [...] }
        or an empty dict on failure.
        """
        params: Dict = {"limit": limit, "page": page}
        if start_date:
            params["start_time"] = start_date
        if end_date:
            params["end_time"] = end_date
        if sticker_num:
            params["sticker_num"] = sticker_num
        if pay_start_time:
            params["pay_start_time"] = pay_start_time
        if pay_end_time:
            params["pay_end_time"] = pay_end_time

        body = self._get("/open/order", params=params)
        if body and body.get("data"):
            return body["data"]
        return {}

    def get_all_paid_orders(self,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            max_pages: int = 20) -> List[Dict]:
        """
        Fetch all paid orders (status=101) across multiple pages.

        Stops after max_pages to avoid very long requests.
        Returns a flat list of order dicts.
        """
        cache_key = f"paid_orders_{start_date}_{end_date}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached  # type: ignore

        all_orders: List[Dict] = []
        page = 1
        while page <= max_pages:
            data = self.get_orders(
                page=page, limit=100,
                start_date=start_date, end_date=end_date
            )
            if not data:
                break
            orders = data.get("list", [])
            # Keep only paid orders
            paid = [o for o in orders if o.get("status") == 101]
            all_orders.extend(paid)

            page_count = data.get("pageCount", 1)
            if page >= page_count:
                break
            page += 1

        self._cache_set(cache_key, all_orders)
        logger.info("HAHA API: fetched %d paid orders (pages 1-%d)", len(all_orders), page)
        return all_orders

    def get_machines_from_orders(self,
                                  days: int = 30) -> List[Dict]:
        """
        Derive the list of unique machines from recent order history.

        Since the HAHA API does not expose a dedicated device-list endpoint
        in the available documentation, we build the machine list by
        collecting unique (sticker_num, device_name) pairs from orders.

        Returns a list of dicts:
          { sticker_num, device_name, order_count, total_revenue, last_order_time }
        """
        cache_key = f"machines_from_orders_{days}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached  # type: ignore

        end_date = datetime.utcnow().strftime("%Y-%m-%d")
        start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Fetch a broader set (all statuses) to identify machines
        all_orders: List[Dict] = []
        page = 1
        while page <= 10:
            data = self.get_orders(page=page, limit=100,
                                   start_date=start_date, end_date=end_date)
            if not data:
                break
            all_orders.extend(data.get("list", []))
            if page >= data.get("pageCount", 1):
                break
            page += 1

        # Aggregate by sticker_num
        machines: Dict[str, Dict] = {}
        for order in all_orders:
            sn = order.get("sticker_num", "")
            dn = order.get("device_name", sn)
            if not sn:
                continue
            if sn not in machines:
                machines[sn] = {
                    "sticker_num": sn,
                    "device_name": dn or sn,
                    "order_count": 0,
                    "total_revenue": 0.0,
                    "last_order_time": None
                }
            machines[sn]["order_count"] += 1
            if order.get("status") == 101:
                try:
                    machines[sn]["total_revenue"] += float(
                        order.get("actual_payment_amount", 0) or 0
                    )
                except (ValueError, TypeError):
                    pass
            ct = order.get("create_time")
            if ct:
                if (machines[sn]["last_order_time"] is None or
                        ct > machines[sn]["last_order_time"]):
                    machines[sn]["last_order_time"] = ct

        result = sorted(machines.values(),
                        key=lambda m: m["total_revenue"], reverse=True)
        self._cache_set(cache_key, result)
        return result

    def get_revenue_summary(self,
                             days: int = 30) -> Dict:
        """
        Return a revenue summary for the last N days.

        Returns:
          {
            total_revenue: float,
            order_count: int,
            daily_revenue: [ { date: str, revenue: float, orders: int }, ... ],
            by_machine: [ { sticker_num, device_name, revenue, orders }, ... ]
          }
        """
        cache_key = f"revenue_summary_{days}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached  # type: ignore

        end_date = datetime.utcnow().strftime("%Y-%m-%d")
        start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        paid_orders = self.get_all_paid_orders(
            start_date=start_date, end_date=end_date, max_pages=20
        )

        daily: Dict[str, Dict] = {}
        by_machine: Dict[str, Dict] = {}
        total_revenue = 0.0

        for order in paid_orders:
            amount = 0.0
            try:
                amount = float(order.get("actual_payment_amount", 0) or 0)
            except (ValueError, TypeError):
                pass

            # Daily aggregation
            pay_time = order.get("pay_time") or order.get("create_time", "")
            date_str = pay_time[:10] if pay_time else "unknown"
            if date_str not in daily:
                daily[date_str] = {"date": date_str, "revenue": 0.0, "orders": 0}
            daily[date_str]["revenue"] += amount
            daily[date_str]["orders"] += 1

            # Per-machine aggregation
            sn = order.get("sticker_num", "unknown")
            dn = order.get("device_name", sn)
            if sn not in by_machine:
                by_machine[sn] = {
                    "sticker_num": sn,
                    "device_name": dn,
                    "revenue": 0.0,
                    "orders": 0
                }
            by_machine[sn]["revenue"] += amount
            by_machine[sn]["orders"] += 1
            total_revenue += amount

        # Round revenue values
        for d in daily.values():
            d["revenue"] = round(d["revenue"], 2)
        for m in by_machine.values():
            m["revenue"] = round(m["revenue"], 2)

        result = {
            "total_revenue": round(total_revenue, 2),
            "order_count": len(paid_orders),
            "daily_revenue": sorted(daily.values(), key=lambda x: x["date"]),
            "by_machine": sorted(by_machine.values(),
                                  key=lambda x: x["revenue"], reverse=True)
        }
        self._cache_set(cache_key, result)
        return result

    def get_recent_orders(self, limit: int = 20) -> List[Dict]:
        """Return the most recent N orders (any status)."""
        data = self.get_orders(page=1, limit=limit)
        return data.get("list", [])

    def clear_cache(self) -> None:
        """Invalidate all cached responses."""
        self._cache.clear()
        logger.info("HAHA API: cache cleared")


# ---------------------------------------------------------------------------
# Legacy mock kept for backward compatibility (not used in production)
# ---------------------------------------------------------------------------

class HAHAVendingAPIMock(HAHAVendingAPI):
    """
    Thin mock subclass — only used when real credentials are unavailable.
    In production the real HAHAVendingAPI is always instantiated.
    """

    def __init__(self, merchant_id: str = "demo_merchant"):
        # Provide dummy credentials; all calls will fail gracefully
        super().__init__(appkey="demo_key", appsecret="demo_secret")
        self.merchant_id = merchant_id

    def authenticate(self) -> bool:
        logger.info("Mock HAHA API: simulated authentication")
        return True

    def get_machines_from_orders(self, days: int = 30) -> List[Dict]:
        return [
            {"sticker_num": "B151690", "device_name": "10X Frozen",
             "order_count": 50, "total_revenue": 450.00, "last_order_time": None},
            {"sticker_num": "B153262", "device_name": "10X Essentials",
             "order_count": 80, "total_revenue": 720.00, "last_order_time": None},
            {"sticker_num": "B153289", "device_name": "10X Fuel",
             "order_count": 65, "total_revenue": 580.00, "last_order_time": None},
            {"sticker_num": "B153295", "device_name": "10X Grab & Go",
             "order_count": 90, "total_revenue": 810.00, "last_order_time": None},
        ]

    def get_revenue_summary(self, days: int = 30) -> Dict:
        today = datetime.utcnow().date()
        daily = []
        for i in range(days):
            d = (today - timedelta(days=i)).isoformat()
            daily.append({"date": d, "revenue": round(50 + i * 2.5, 2), "orders": 10 + i})
        return {
            "total_revenue": round(sum(x["revenue"] for x in daily), 2),
            "order_count": sum(x["orders"] for x in daily),
            "daily_revenue": sorted(daily, key=lambda x: x["date"]),
            "by_machine": self.get_machines_from_orders(days)
        }

    def get_recent_orders(self, limit: int = 20) -> List[Dict]:
        return []


# ---------------------------------------------------------------------------
# HAHADataSyncManager kept for backward compatibility
# ---------------------------------------------------------------------------

class HAHADataSyncManager:
    """Thin wrapper kept so existing app.py import does not break."""

    def __init__(self, haha_api: HAHAVendingAPI, db_client=None):
        self.haha_api = haha_api
        self.db = db_client
        self.last_sync_time: Dict = {}

    def sync_all(self, force: bool = False) -> Dict:
        return {"status": "ok", "message": "Real API — no sync needed"}


__all__ = [
    "HAHAVendingAPI",
    "HAHAVendingAPIMock",
    "HAHADataSyncManager",
]
