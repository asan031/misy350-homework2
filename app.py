import streamlit as st
import json
from pathlib import Path
import uuid

st.set_page_config(page_title="Smart Coffee Kiosk", layout="wide")

json_file = Path("inventory.json")

if json_file.exists():
    with open(json_file, "r") as f:
        inventory = json.load(f)
else:
    inventory = []

def save_inventory():
    with open(json_file, "w") as f:
        json.dump(inventory, f, indent=4)

if "orders" not in st.session_state:
    st.session_state.orders = []

st.title("Smart Coffee Kiosk")
st.write("Manage inventory and customer orders")

tab1, tab2, tab3, tab4 = st.tabs([
    "Place Order",
    "View Inventory",
    "Restock",
    "Manage Orders"
])

with tab1:
    st.header("Place Order")

    if inventory:
        item_names = [item["name"] for item in inventory]
        selected_name = st.selectbox("Select Item", item_names)

        selected_item = None
        for item in inventory:
            if item["name"] == selected_name:
                selected_item = item

        quantity = st.number_input("Quantity", min_value=1, step=1)
        customer_name = st.text_input("Customer Name")

        if st.button("Place Order"):
            if customer_name.strip() == "":
                st.error("Please enter a customer name.")
            elif selected_item["stock"] >= quantity:
                selected_item["stock"] -= quantity
                total_price = selected_item["price"] * quantity

                order = {
                    "order_id": str(uuid.uuid4())[:8],
                    "customer": customer_name,
                    "item": selected_item["name"],
                    "quantity": quantity,
                    "total": total_price,
                    "status": "Placed"
                }

                st.session_state.orders.append(order)
                save_inventory()

                st.success("Order Placed")

                with st.expander("View Receipt"):
                    st.write(f"Order ID: {order['order_id']}")
                    st.write(f"Customer: {order['customer']}")
                    st.write(f"Item: {order['item']}")
                    st.write(f"Quantity: {order['quantity']}")
                    st.write(f"Total: ${order['total']:.2f}")
                    st.write(f"Status: {order['status']}")
            else:
                st.error("Out of Stock")
    else:
        st.warning("Inventory is empty.")

with tab2:
    st.header("View & Search Inventory")

    search = st.text_input("Search for an item")

    total_stock = 0
    for item in inventory:
        total_stock += item["stock"]

    st.metric("Total Items in Stock", total_stock)

    filtered_inventory = []
    for item in inventory:
        if search.lower() in item["name"].lower():
            filtered_inventory.append(item)

    if filtered_inventory:
        for item in filtered_inventory:
            if item["stock"] < 10:
                st.warning(
                    f"ID: {item['id']} | {item['name']} | Price: ${item['price']:.2f} | Stock: {item['stock']}"
                )
            else:
                st.write(
                    f"ID: {item['id']} | {item['name']} | Price: ${item['price']:.2f} | Stock: {item['stock']}"
                )
    else:
        st.write("No matching items found.")

with tab3:
    st.header("Restock Inventory")

    if inventory:
        restock_name = st.selectbox(
            "Select Item to Restock",
            [item["name"] for item in inventory],
            key="restock_select"
        )

        restock_amount = st.number_input(
            "Add Stock Amount",
            min_value=1,
            step=1,
            key="restock_amount"
        )

        if st.button("Update Stock"):
            for item in inventory:
                if item["name"] == restock_name:
                    item["stock"] += restock_amount
                    save_inventory()
                    st.success(f"{restock_name} restocked successfully")
                    break
    else:
        st.warning("Inventory is empty.")

with tab4:
    st.header("Manage Orders")

    if st.session_state.orders:
        for order in st.session_state.orders:
            st.write(
                f"Order ID: {order['order_id']} | Customer: {order['customer']} | "
                f"Item: {order['item']} | Quantity: {order['quantity']} | "
                f"Total: ${order['total']:.2f} | Status: {order['status']}"
            )

        active_orders = []
        for order in st.session_state.orders:
            if order["status"] == "Placed":
                active_orders.append(order)

        if active_orders:
            cancel_order_id = st.selectbox(
                "Select Order to Cancel",
                [order["order_id"] for order in active_orders]
            )

            if st.button("Cancel Order"):
                for order in st.session_state.orders:
                    if order["order_id"] == cancel_order_id and order["status"] == "Placed":
                        order["status"] = "Cancelled"

                        for item in inventory:
                            if item["name"] == order["item"]:
                                item["stock"] += order["quantity"]
                                break

                        save_inventory()
                        st.success("Order Cancelled and Stock Refunded")
                        break
        else:
            st.write("No active orders to cancel.")
    else:
        st.write("No orders placed yet.")