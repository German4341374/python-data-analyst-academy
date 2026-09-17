import io
import json
import zipfile

import pandas as pd
import pytest

from academy.datasets import (
    CustomerGenerator,
    EcommerceGenerator,
    GeneratorConfig,
    MarketingGenerator,
    SalesGenerator,
    SupportTicketsGenerator,
    project_archive,
)


@pytest.mark.parametrize(
    "generator", [SalesGenerator, CustomerGenerator, MarketingGenerator, SupportTicketsGenerator]
)
def test_generators_are_reproducible(generator):
    config = GeneratorConfig(rows=30, seed=31)
    pd.testing.assert_frame_equal(generator().generate(config), generator().generate(config))


def test_relational_dataset_integrity():
    tables = EcommerceGenerator().generate(GeneratorConfig())
    customers, orders, items, products = (
        tables[name] for name in ["customers.csv", "orders.csv", "order_items.csv", "products.csv"]
    )
    assert customers.customer_id.is_unique and products.product_id.is_unique
    assert items.item_id.is_unique
    assert set(orders.customer_id) <= set(customers.customer_id)
    assert set(items.order_id) <= set(orders.order_id)
    assert set(items.product_id) <= set(products.product_id)
    assert items.order_id.duplicated().any()  # Genuine multi-item orders.


@pytest.mark.parametrize(
    "identity", ["sales-analysis", "customer-analysis", "marketing-funnel", "ecommerce"]
)
def test_project_archives_have_documented_real_csv(identity):
    with zipfile.ZipFile(io.BytesIO(project_archive(identity))) as archive:
        metadata = json.loads(archive.read("data-dictionary.json"))
        assert metadata["synthetic"] and metadata["seed"] == 2026
        for name, dictionary in metadata["tables"].items():
            df = pd.read_csv(io.BytesIO(archive.read(name)))
            assert len(df) > 0 and set(df.columns) == set(dictionary)


def test_funnel_constraints():
    df = MarketingGenerator().generate(GeneratorConfig())
    assert (df.visits >= df.registrations).all()
    assert (df.registrations >= df.purchases).all()
    assert (df.purchases >= 0).all()
