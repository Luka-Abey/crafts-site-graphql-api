from datetime import date, timedelta

import graphene
import pytest
from freezegun import freeze_time

from ....product.models import Product
from ...tests.utils import get_graphql_content

COLLECTION_RESORT_QUERY = """
mutation ReorderCollectionProducts($collectionId: ID!, $moves: [MoveProductInput]!) {
  collectionReorderProducts(collectionId: $collectionId, moves: $moves) {
    collection {
      id
      products(first: 10, sortBy:{field:COLLECTION, direction:ASC}) {
        edges {
          node {
            name
            id
          }
        }
      }
    }
    errors {
      field
      message
    }
  }
}
"""


def test_sort_products_within_collection_invalid_collection_id(
    staff_api_client, collection, product, permission_manage_products
):
    collection_id = graphene.Node.to_global_id("Collection", -1)
    product_id = graphene.Node.to_global_id("Product", product.pk)

    moves = [{"productId": product_id, "sortOrder": 1}]

    content = get_graphql_content(
        staff_api_client.post_graphql(
            COLLECTION_RESORT_QUERY,
            {"collectionId": collection_id, "moves": moves},
            permissions=[permission_manage_products],
        )
    )["data"]["collectionReorderProducts"]

    assert content["errors"] == [
        {
            "field": "collectionId",
            "message": f"Couldn't resolve to a collection: {collection_id}",
        }
    ]


def test_sort_products_within_collection_invalid_product_id(
    staff_api_client, collection, product, permission_manage_products
):
    # Remove the products from the collection to make the product invalid
    collection.products.clear()
    collection_id = graphene.Node.to_global_id("Collection", collection.pk)

    # The move should be targeting an invalid product
    product_id = graphene.Node.to_global_id("Product", product.pk)
    moves = [{"productId": product_id, "sortOrder": 1}]

    content = get_graphql_content(
        staff_api_client.post_graphql(
            COLLECTION_RESORT_QUERY,
            {"collectionId": collection_id, "moves": moves},
            permissions=[permission_manage_products],
        )
    )["data"]["collectionReorderProducts"]

    assert content["errors"] == [
        {"field": "moves", "message": f"Couldn't resolve to a product: {product_id}"}
    ]


def test_sort_products_within_collection(
    staff_api_client,
    staff_user,
    collection,
    collection_with_products,
    permission_manage_products,
):

    staff_api_client.user.user_permissions.add(permission_manage_products)
    collection_id = graphene.Node.to_global_id("Collection", collection.pk)

    products = collection_with_products
    product = graphene.Node.to_global_id("Product", products[0].pk)
    second_product = graphene.Node.to_global_id("Product", products[1].pk)
    third_product = graphene.Node.to_global_id("Product", products[2].pk)

    variables = {
        "collectionId": collection_id,
        "moves": [{"productId": product, "sortOrder": -1}],
    }

    content = get_graphql_content(
        staff_api_client.post_graphql(COLLECTION_RESORT_QUERY, variables)
    )["data"]["collectionReorderProducts"]
    assert not content["errors"]

    assert content["collection"]["id"] == collection_id

    products = content["collection"]["products"]["edges"]
    assert products[0]["node"]["id"] == product
    assert products[1]["node"]["id"] == third_product
    assert products[2]["node"]["id"] == second_product

    variables = {
        "collectionId": collection_id,
        "moves": [{"productId": product, "sortOrder": 1}],
    }
    content = get_graphql_content(
        staff_api_client.post_graphql(COLLECTION_RESORT_QUERY, variables)
    )["data"]["collectionReorderProducts"]

    products = content["collection"]["products"]["edges"]
    assert products[0]["node"]["id"] == third_product
    assert products[1]["node"]["id"] == product
    assert products[2]["node"]["id"] == second_product


GET_SORTED_PRODUCTS_QUERY = """
query Products($sortBy: ProductOrder) {
    products(first: 10, sortBy: $sortBy) {
      edges {
        node {
          id
          publicationDate
        }
      }
    }
}
"""


@freeze_time("2020-03-18 12:00:00")
@pytest.mark.parametrize(
    "direction, order_direction",
    (("ASC", "publication_date"), ("DESC", "-publication_date")),
)
def test_sort_products_by_publication_date(
    direction, order_direction, staff_api_client, product_list
):

    for iter_value, product in enumerate(product_list):
        product.publication_date = date.today() - timedelta(days=iter_value)
    Product.objects.bulk_update(product_list, ["publication_date"])

    variables = {
        "sortBy": {"direction": direction, "field": "PUBLICATION_DATE"},
    }

    # when
    response = staff_api_client.post_graphql(GET_SORTED_PRODUCTS_QUERY, variables)

    # then
    content = get_graphql_content(response)
    data = content["data"]["products"]["edges"]

    assert [node["node"]["id"] for node in data] == [
        graphene.Node.to_global_id("Product", product.pk)
        for product in Product.objects.order_by(order_direction)
    ]
