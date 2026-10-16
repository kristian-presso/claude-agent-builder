# What people ask the clinic assistant (from last month's transcripts)

- "Can you move my Thursday physio to next week, same time if possible?" (most common)
- "Book me in with Sam for a sports massage, any evening next week"
- "Cancel my appointment tomorrow"
- "Has my last invoice been paid?"
- "What times does Dr Okafor have free on Monday?"

Observed: rescheduling takes the model 6 to 9 tool calls (list_customers, get_customer,
list_appointments, get_appointment, list_availability_slots, update_appointment...). It
often picks update_availability_slot instead of update_appointment, and twice called
delete_appointment then create_appointment, losing the original booking's deposit.
