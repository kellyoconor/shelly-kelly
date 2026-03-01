---
name: package-tracker
description: "Track packages and deliveries. Automatically extracts tracking numbers from forwarded emails, checks carrier status, and alerts on updates."
metadata: { "openclaw": { "emoji": "📦" } }
---

# Package Tracker

## How It Works
1. Kelly forwards order/shipping emails to shelly@agentmail.to
2. Shelly extracts tracking numbers + carrier info
3. Status is saved to `data/packages.json`
4. Cron job checks for updates and alerts Kelly on WhatsApp

## Supported Carriers
- USPS (starts with 94, 92, or 20-30 digits)
- UPS (starts with 1Z)
- FedEx (12-22 digits)
- DHL (10 digits)
- Amazon (TBA)

## Data File
`data/packages.json` — array of package objects:
```json
{
  "id": "uuid",
  "name": "WHOOP Order",
  "carrier": "usps",
  "tracking": "1234567890",
  "status": "in_transit",
  "lastUpdate": "2026-03-01T20:00:00Z",
  "estimatedDelivery": null,
  "delivered": false,
  "addedAt": "2026-03-01T20:00:00Z",
  "emailThreadId": "thread-id"
}
```

## Status Values
- `ordered` — confirmed but not shipped
- `shipped` — label created
- `in_transit` — on the way
- `out_for_delivery` — arriving today!
- `delivered` — done
- `delayed` — issue detected
- `unknown` — can't determine

## Alerts
- **Out for delivery** → immediate WhatsApp message
- **Delivered** → WhatsApp message
- **Delayed** → WhatsApp message
- **Daily summary** → included in morning briefing if active packages exist

## Checking Status
Use carrier tracking pages via web_fetch to scrape current status.
- USPS: https://tools.usps.com/go/TrackConfirmAction?tLabels=TRACKING
- UPS: https://www.ups.com/track?tracknum=TRACKING
- FedEx: https://www.fedex.com/fedextrack/?trknbr=TRACKING

## Commands
- "check my packages" → show all active packages
- "track this" + forwarded email → extract and add tracking
- "remove package X" → mark as done/remove
