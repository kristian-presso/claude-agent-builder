"""Clinic MCP server: one tool per REST endpoint of our booking API (generated from the OpenAPI spec)."""

from mcp.server.fastmcp import FastMCP

from clinic_api import api

mcp = FastMCP("clinic")

@mcp.tool()
def get_customer(customer_id: int) -> dict:
    """Get a customer record by id."""
    return api.get("customers", customer_id)

@mcp.tool()
def list_customers(page: int = 1, page_size: int = 50) -> dict:
    """List a customer records. Supports page and page_size."""
    return api.list("customers", page, page_size)

@mcp.tool()
def create_customer(fields: dict) -> dict:
    """Create a customer record. Fields as in the REST API."""
    return api.create("customers", fields)

@mcp.tool()
def update_customer(customer_id: int, fields: dict) -> dict:
    """Update a customer record by id. Fields as in the REST API."""
    return api.update("customers", customer_id, fields)

@mcp.tool()
def delete_customer(customer_id: int) -> dict:
    """Delete a customer record by id."""
    return api.delete("customers", customer_id)

@mcp.tool()
def get_appointment(appointment_id: int) -> dict:
    """Get an appointment by id."""
    return api.get("appointments", appointment_id)

@mcp.tool()
def list_appointments(page: int = 1, page_size: int = 50) -> dict:
    """List an appointments. Supports page and page_size."""
    return api.list("appointments", page, page_size)

@mcp.tool()
def create_appointment(fields: dict) -> dict:
    """Create an appointment. Fields as in the REST API."""
    return api.create("appointments", fields)

@mcp.tool()
def update_appointment(appointment_id: int, fields: dict) -> dict:
    """Update an appointment by id. Fields as in the REST API."""
    return api.update("appointments", appointment_id, fields)

@mcp.tool()
def delete_appointment(appointment_id: int) -> dict:
    """Delete an appointment by id."""
    return api.delete("appointments", appointment_id)

@mcp.tool()
def get_staff(staff_id: int) -> dict:
    """Get a staff member by id."""
    return api.get("staffs", staff_id)

@mcp.tool()
def list_staffs(page: int = 1, page_size: int = 50) -> dict:
    """List a staff members. Supports page and page_size."""
    return api.list("staffs", page, page_size)

@mcp.tool()
def create_staff(fields: dict) -> dict:
    """Create a staff member. Fields as in the REST API."""
    return api.create("staffs", fields)

@mcp.tool()
def update_staff(staff_id: int, fields: dict) -> dict:
    """Update a staff member by id. Fields as in the REST API."""
    return api.update("staffs", staff_id, fields)

@mcp.tool()
def delete_staff(staff_id: int) -> dict:
    """Delete a staff member by id."""
    return api.delete("staffs", staff_id)

@mcp.tool()
def get_service(service_id: int) -> dict:
    """Get a service on the menu by id."""
    return api.get("services", service_id)

@mcp.tool()
def list_services(page: int = 1, page_size: int = 50) -> dict:
    """List a service on the menus. Supports page and page_size."""
    return api.list("services", page, page_size)

@mcp.tool()
def create_service(fields: dict) -> dict:
    """Create a service on the menu. Fields as in the REST API."""
    return api.create("services", fields)

@mcp.tool()
def update_service(service_id: int, fields: dict) -> dict:
    """Update a service on the menu by id. Fields as in the REST API."""
    return api.update("services", service_id, fields)

@mcp.tool()
def delete_service(service_id: int) -> dict:
    """Delete a service on the menu by id."""
    return api.delete("services", service_id)

@mcp.tool()
def get_room(room_id: int) -> dict:
    """Get a treatment room by id."""
    return api.get("rooms", room_id)

@mcp.tool()
def list_rooms(page: int = 1, page_size: int = 50) -> dict:
    """List a treatment rooms. Supports page and page_size."""
    return api.list("rooms", page, page_size)

@mcp.tool()
def create_room(fields: dict) -> dict:
    """Create a treatment room. Fields as in the REST API."""
    return api.create("rooms", fields)

@mcp.tool()
def update_room(room_id: int, fields: dict) -> dict:
    """Update a treatment room by id. Fields as in the REST API."""
    return api.update("rooms", room_id, fields)

@mcp.tool()
def delete_room(room_id: int) -> dict:
    """Delete a treatment room by id."""
    return api.delete("rooms", room_id)

@mcp.tool()
def get_availability_slot(availability_slot_id: int) -> dict:
    """Get an availability slot by id."""
    return api.get("availability_slots", availability_slot_id)

@mcp.tool()
def list_availability_slots(page: int = 1, page_size: int = 50) -> dict:
    """List an availability slots. Supports page and page_size."""
    return api.list("availability_slots", page, page_size)

@mcp.tool()
def create_availability_slot(fields: dict) -> dict:
    """Create an availability slot. Fields as in the REST API."""
    return api.create("availability_slots", fields)

@mcp.tool()
def update_availability_slot(availability_slot_id: int, fields: dict) -> dict:
    """Update an availability slot by id. Fields as in the REST API."""
    return api.update("availability_slots", availability_slot_id, fields)

@mcp.tool()
def delete_availability_slot(availability_slot_id: int) -> dict:
    """Delete an availability slot by id."""
    return api.delete("availability_slots", availability_slot_id)

@mcp.tool()
def get_payment(payment_id: int) -> dict:
    """Get a payment by id."""
    return api.get("payments", payment_id)

@mcp.tool()
def list_payments(page: int = 1, page_size: int = 50) -> dict:
    """List a payments. Supports page and page_size."""
    return api.list("payments", page, page_size)

@mcp.tool()
def create_payment(fields: dict) -> dict:
    """Create a payment. Fields as in the REST API."""
    return api.create("payments", fields)

@mcp.tool()
def update_payment(payment_id: int, fields: dict) -> dict:
    """Update a payment by id. Fields as in the REST API."""
    return api.update("payments", payment_id, fields)

@mcp.tool()
def delete_payment(payment_id: int) -> dict:
    """Delete a payment by id."""
    return api.delete("payments", payment_id)

@mcp.tool()
def get_note(note_id: int) -> dict:
    """Get a note on a customer by id."""
    return api.get("notes", note_id)

@mcp.tool()
def list_notes(page: int = 1, page_size: int = 50) -> dict:
    """List a note on a customers. Supports page and page_size."""
    return api.list("notes", page, page_size)

@mcp.tool()
def create_note(fields: dict) -> dict:
    """Create a note on a customer. Fields as in the REST API."""
    return api.create("notes", fields)

@mcp.tool()
def update_note(note_id: int, fields: dict) -> dict:
    """Update a note on a customer by id. Fields as in the REST API."""
    return api.update("notes", note_id, fields)

@mcp.tool()
def delete_note(note_id: int) -> dict:
    """Delete a note on a customer by id."""
    return api.delete("notes", note_id)

if __name__ == "__main__":
    mcp.run()
