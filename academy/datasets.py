"""Deterministic synthetic business datasets; never contains real customer data."""

import io
import json
import zipfile
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class GeneratorConfig:
    rows: int = 120
    seed: int = 2026
    missing_ratio: float = 0.03
    duplicate_ratio: float = 0.05
    categories: tuple[str, ...] = ("Riga", "Tallinn", "Vilnius", "Berlin")
    start: date = field(default_factory=lambda: date(2026, 1, 1))
    end: date = field(default_factory=lambda: date(2026, 6, 30))
    outliers: bool = True

    def __post_init__(self):
        if not 1 <= self.rows <= 10000 or not self.categories or self.start > self.end:
            raise ValueError("Invalid row count, categories or date range")
        if not 0 <= self.missing_ratio < 1 or not 0 <= self.duplicate_ratio < 1:
            raise ValueError("Ratios must be in [0, 1)")


class SalesGenerator:
    def generate(self, config: GeneratorConfig) -> pd.DataFrame:
        rng = np.random.default_rng(config.seed)
        size = config.rows
        df = pd.DataFrame(
            {
                "order_id": np.arange(1, size + 1),
                "customer_id": rng.integers(1, max(3, size // 3) + 1, size),
                "order_date": [
                    str(config.start + pd.Timedelta(days=int(x)))
                    for x in rng.integers(0, (config.end - config.start).days + 1, size)
                ],
                "city": rng.choice(config.categories, size).astype(object),
                "quantity": rng.integers(1, 6, size),
                "price": np.round(rng.uniform(5, 200, size), 2),
                "status": rng.choice(["paid", "cancelled"], size, p=[0.88, 0.12]),
            }
        )
        missing = rng.choice(size, int(size * config.missing_ratio), replace=False)
        df.loc[missing, "city"] = None
        if size >= 10:
            df.loc[1, "city"] = f" {config.categories[0].upper()} "
            df.loc[2, "price"] = -10.0  # Documented invalid price for audit practice.
        if config.outliers:
            df.loc[size - 1, "price"] = (
                2400.0  # Valid rare large order, not automatically an error.
            )
        count = int(size * config.duplicate_ratio)
        return pd.concat([df, df.iloc[:count]], ignore_index=True)


class CustomerGenerator:
    def generate(self, config: GeneratorConfig) -> pd.DataFrame:
        rng = np.random.default_rng(config.seed)
        size = max(3, config.rows // 3)
        df = pd.DataFrame(
            {
                "customer_id": np.arange(1, size + 1),
                "city": rng.choice(config.categories, size),
                "segment": rng.choice(["new", "regular", "loyal"], size),
            }
        )
        return df


class MarketingGenerator:
    def generate(self, config: GeneratorConfig) -> pd.DataFrame:
        rng = np.random.default_rng(config.seed)
        visits = rng.integers(0, 5000, config.rows)
        registrations = rng.binomial(visits, 0.23)
        purchases = rng.binomial(registrations, 0.31)
        return pd.DataFrame(
            {
                "day": [
                    str(config.start + pd.Timedelta(days=int(x)))
                    for x in rng.integers(0, (config.end - config.start).days + 1, config.rows)
                ],
                "channel": rng.choice(["organic", "search", "referral"], config.rows),
                "visits": visits,
                "registrations": registrations,
                "purchases": purchases,
            }
        )


class SupportTicketsGenerator:
    def generate(self, config: GeneratorConfig) -> pd.DataFrame:
        rng = np.random.default_rng(config.seed)
        minutes = np.round(rng.lognormal(3, 0.7, config.rows), 1)
        minutes[: int(config.rows * config.missing_ratio)] = np.nan
        if config.outliers:
            minutes[-1] = 2000
        df = pd.DataFrame(
            {
                "ticket_id": np.arange(1, config.rows + 1),
                "category": rng.choice(config.categories, config.rows),
                "resolution_minutes": minutes,
            }
        )
        return pd.concat(
            [df, df.head(int(config.rows * config.duplicate_ratio))], ignore_index=True
        )


class EcommerceGenerator:
    def generate(self, config: GeneratorConfig) -> dict[str, pd.DataFrame]:
        orders = SalesGenerator().generate(config)
        customers = CustomerGenerator().generate(config)
        products = pd.DataFrame(
            {
                "product_id": range(1, 7),
                "product_name": [
                    "Desk lamp",
                    "Notebook",
                    "Coffee beans",
                    "Cable",
                    "Mug",
                    "Backpack",
                ],
                "category": ["Home", "Office", "Food", "Electronics", "Home", "Travel"],
            }
        )
        rng = np.random.default_rng(config.seed + 1)
        clean_orders = orders.drop_duplicates("order_id")
        items = pd.DataFrame(
            {
                "item_id": range(1, len(clean_orders) + 1),
                "order_id": clean_orders.order_id,
                "product_id": rng.integers(1, 7, len(clean_orders)),
                "quantity": clean_orders.quantity,
                "unit_price": clean_orders.price,
            }
        )
        extra = items.iloc[:20].copy()
        extra["item_id"] = np.arange(len(items) + 1, len(items) + len(extra) + 1)
        extra["quantity"] = 1
        items = pd.concat([items, extra], ignore_index=True)
        return {
            "orders.csv": orders[["order_id", "customer_id", "order_date", "status"]],
            "customers.csv": customers,
            "products.csv": products,
            "order_items.csv": items,
        }


DICTIONARY: dict[str, str] = {
    "order_id": "Order key. Repeated IDs in orders are intentionally duplicated records; in order_items multiple rows per order are valid.",
    "customer_id": "Synthetic customer key; customers.customer_id is unique.",
    "order_date": "Order date, YYYY-MM-DD.",
    "city": "Customer/order city; spaces, capitalization and missing values may require cleaning.",
    "quantity": "Number of units in an order line.",
    "price": "Unit price in EUR in the single-line sales dataset. Negative values are intentional errors.",
    "unit_price": "Price per unit in EUR for each item; negative values are intentional data-quality errors.",
    "status": "paid or cancelled. Define whether cancelled orders belong in each metric.",
    "segment": "Synthetic customer segment, not a causal or predictive label.",
    "item_id": "Unique order line key.",
    "product_id": "Product key referencing products.csv.",
    "product_name": "Synthetic product label.",
    "category": "Product or support category.",
    "day": "Observation date, YYYY-MM-DD.",
    "channel": "Synthetic acquisition channel.",
    "visits": "Nonnegative visits for the day/channel observation.",
    "registrations": "Registrations, no greater than visits.",
    "purchases": "Purchases, no greater than registrations.",
}


def project_archive(project_id: str) -> bytes:
    config = GeneratorConfig()
    if project_id == "ecommerce":
        tables = EcommerceGenerator().generate(config)
    elif project_id == "marketing-funnel":
        tables = {"marketing.csv": MarketingGenerator().generate(config)}
    elif project_id == "customer-analysis":
        tables = {
            "customers.csv": CustomerGenerator().generate(config),
            "orders.csv": SalesGenerator().generate(config),
        }
    elif project_id == "sales-analysis":
        tables = {"orders.csv": SalesGenerator().generate(config)}
    else:
        raise KeyError(project_id)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, table in tables.items():
            archive.writestr(name, table.to_csv(index=False))
        metadata: dict[str, Any] = {
            "version": 1,
            "seed": config.seed,
            "license": "MIT",
            "synthetic": True,
            "currency": "EUR",
            "tables": {
                name: {column: DICTIONARY[column] for column in table.columns}
                for name, table in tables.items()
            },
            "intentional_quality_issues": [
                "Sales orders include repeated order_id records, missing city values, inconsistent city formatting, one negative price and cancelled orders.",
                "E-commerce order_items has valid many-to-one relationships with orders; repeated order_id in items is not a duplicate line.",
                "A rare large positive price is valid. Do not automatically remove outliers.",
            ],
        }
        archive.writestr("data-dictionary.json", json.dumps(metadata, ensure_ascii=False, indent=2))
        archive.writestr(
            "README.txt",
            "Synthetic educational data. No real people. UTF-8 CSV; comma separator; decimal point.\nRead data-dictionary.json before analysis. Keep raw files unchanged.\nRevenue excludes taxes/shipping/returns not represented in this schema.\n",
        )
    return buffer.getvalue()
