# Create Subscription API

## Endpoint

`POST /api/subscriptions/`

## Description

This endpoint creates a new subscription for a user. If the user already exists, it updates the email address in both the local database and Stripe if necessary. A new Stripe customer is created if the user does not already have one. Finally, a subscription is created for the specified price plan.

## Request

### Headers

- `Content-Type: application/json`

### Request Body

```json
{
  "user_id": "string",
  "email": "string",
  "payment_method_id": "string",
  "price_id": "string"
}
