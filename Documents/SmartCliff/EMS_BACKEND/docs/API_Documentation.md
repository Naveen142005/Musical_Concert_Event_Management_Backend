# FastAPI API Documentation

**Version:** 0.1.0

**Generated on:** 2025-10-31 15:50:36


---
API Documentation
---


## `/signup`

### POST: Signup

**Description:** 

**Tags:** Users


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/Login`

### POST: Login

**Description:** 

**Tags:** Users


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/facilities/venues`

### GET: Get All Venues

**Description:** 

**Tags:** Facilities


**Parameters:**

- `name` (query) — Show venues only by the Names.

- `location` (query) — Show venues only from this location (can match partly).

- `min_capacity` (query) — Show venues with at least this much capacity.

- `max_price` (query) — Show only items with price less than or equal to this value.

- `sort_by` (query) — Sort by this column name (like price, name, or capacity).

- `order` (query) — Sort order — 'asc' for ascending, 'desc' for descending.


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/facilities/bands`

### GET: Get All Bands

**Description:** 

**Tags:** Facilities


**Parameters:**

- `name` (query) — Filter bands by name.

- `genre` (query) — Filter bands by genre.

- `member_count` (query) — Filter bands by member count.

- `max_price` (query) — Show only bands with price less than or equal to this value.

- `sort_by` (query) — Sort by this column name (like price, name, or member_count).

- `order` (query) — Sort order — 'asc' or 'desc'.


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/facilities/decorations`

### GET: Get All Decorations

**Description:** 

**Tags:** Facilities


**Parameters:**

- `name` (query) — Filter decorations by name.

- `type` (query) — Filter decorations by type.

- `max_price` (query) — Show only decorations with price less than or equal to this value.

- `sort_by` (query) — Sort by this column name (like price or name).

- `order` (query) — Sort order — 'asc' or 'desc'.


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/facilities/snacks`

### GET: Get All Snacks

**Description:** 

**Tags:** Facilities


**Parameters:**

- `price` (query) — Filter snacks by price.

- `sort_by` (query) — Sort by this column name (like price or id).

- `order` (query) — Sort order — 'asc' or 'desc'.


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/events/create_new_event`

### POST: Create New Event

**Description:** 

**Tags:** Events


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/events/facility/`

### GET: Check Facility Available

**Description:** 

**Tags:** Events


**Parameters:**

- `id` (query) — Facility ID

- `facility_name` (query) — Name of the facility

- `date` (query) — Expected date of the facility

- `slot` (query) — Slot of the facility (Morning/Afternoon/Night)


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/events/myBookings`

### GET: Get My Bookings

**Description:** 

**Tags:** Events


**Responses:**

- `200` — Successful Response


---


## `/events/event_by_id/{event_id}`

### GET: Get Event By Id

**Description:** 

**Tags:** Events


**Parameters:**

- `event_id` (path) — 


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/events/update_banner`

### PATCH: Update Banner

**Description:** 

**Tags:** Events


**Parameters:**

- `eventId` (query) — Event Id


**Request Body Example:**


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/events/get_reschedule_dates`

### GET: Get Possible Reschedule Dates

**Description:** 

**Tags:** Events


**Parameters:**

- `eventId` (query) — Event Id

- `start_date` (query) — Start date in YYYY-MM-DD 

- `end_date` (query) — End date in YYYY-MM-DD 

- `slot` (query) — Slot of the facility (Morning/Afternoon/Night)


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---


## `/events/facilities`

### GET: Check Facilities Available

**Description:** 

**Tags:** Events


**Parameters:**

- `slot` (query) — Slot of the facility (Morning/Afternoon/Night)

- `venue_id` (query) — venue ID

- `band_id` (query) — Band ID

- `decoration_id` (query) — Decoration ID

- `no_days` (query) — upto, how many days


**Responses:**

- `200` — Successful Response

- `422` — Validation Error


---
