from biteharbor.domain import extract_identifier, filter_menu, lookup_order


def test_extracts_supported_identifiers():
    assert extract_identifier("Track ORD-201") == "ORD-201"
    assert extract_identifier("Tracking is BH202TRK") == "BH202TRK"
    assert extract_identifier("Use priya@example.com") == "priya@example.com"


def test_indian_food_under_300_applies_exact_constraints():
    matches = filter_menu("Indian food under 300")
    assert {item["name"] for item in matches} == {"Paneer Tikka", "Mango Lassi"}


def test_vegan_implies_vegetarian_but_not_the_reverse():
    matches = filter_menu("vegetarian food")
    names = {item["name"] for item in matches}
    assert "Vegan Buddha Bowl" in names
    assert "Paneer Tikka" in names
    assert "Butter Chicken" not in names


def test_butter_chicken_is_not_claimed_gluten_free():
    matches = filter_menu("gluten free Indian food")
    assert "Butter Chicken" not in {item["name"] for item in matches}


def test_order_lookup_is_scoped_to_trusted_customer():
    assert lookup_order("ORD-201", "demo-priya")["status"] == "Out for Delivery"
    assert lookup_order("ORD-201", "demo-arjun") == {
        "error": "No matching order was found for this customer."
    }


def test_order_lookup_does_not_return_customer_pii():
    result = lookup_order("priya@example.com", "demo-priya")
    assert "customer_email" not in result
    assert "customer_name" not in result
    assert "customer_id" not in result
