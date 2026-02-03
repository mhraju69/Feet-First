# Pro Stock & Inventory Management System (Feet First)

This document is the definitive technical and operational guide for the stock and inventory engine of the Feet First platform. It covers everything from granular database schema to complex business logic for multi-vendor distribution.

---

## 1. Core Inventory Philosophy
The system operates on a **Single Catalog, Multi-Fulfillment** model. 
- **Global Standard**: A standardized product catalog (`Product`) ensures data consistency.
- **Partner Flexibility**: Partners (vendors) maintain their own prices, color variants, and stock levels.
- **Granular Availability**: Stock is tracked at the **Product-Color-Size-Partner** level.

---

## 2. Technical Data Architecture

### 2.1 The Four Pillars of Stock
1.  **`Product` (Global)**: The parent entry. Contains name, brand, gender, and technical data.
2.  **`PartnerProduct` (Vendor Variant)**: The link between a partner and a specific color version of a product. 
3.  **`PartnerProductSize` (Granular Stock)**: The actual quantity available for a specific size of a `PartnerProduct`.
4.  **`Warehouse` (Physical Location)**: Tracks where the stock is physically stored.

### 2.2 Model Specifications (Products App)
- **`total_stock_quantity` (Property)**: Dynamically calculates the sum of all `PartnerProductSize` quantities for a specific variant. Used for "In Stock" vs. "Out of Stock" labels.
- **`is_active` vs. `online` vs. `local`**:
    -   `is_active`: Overall master switch.
    -   `online`: Product is eligible for the global "Shoe Finder" and sizing matches.
    -   `local`: Product is only available via direct partner listing or local search.

---

## 3. The Eligibility Engine (Online vs. Local)

The system automatically categorizes stock based on standard compliance to ensure users get reliable recommendations.

### 3.1 Online Eligibility Criteria
A product is automatically marked as **Local-Only (`online=False`)** if any of these conditions are met:
1.  **Image Gap**: No global `ProductImage` exists for the specific color.
2.  **Unofficial Sizes**: The partner is stocking a size that is not part of the manufacturer's official `SizeTable` for that model.
3.  **Measurement Gap**: The size stocked lacks `insole_min_mm` or `insole_max_mm` data required for the "Match Score" algorithm.

### 3.2 "Local Sizes" Fallback
If a partner imports a size that does not exist globally:
-   The system creates a **`Local SizeTable`** specifically for that partner/brand.
-   The product variant is restricted to `online=False` to prevent inaccurate sizing recommendations in the "Shoe Finder."

---

## 4. Operational Workflows

### 4.1 Batch Import Engine (The Pro Importer)
The system features a robust CSV/XLSX processing engine in `FileUploadPartnerProductView`:
-   **Smart Matching**: Matches products by exact or fuzzy name.
-   **Auto-Creation**: If an item isn't in the catalog, it creates a "Local" product entry to allow immediate selling.
-   **Column Normalization**:
    -   Prices: Cleaned of currency symbols and commas (`clean_price`).
    -   Sizes: Automatically maps columns like `Size EU` or `size_us` to `s_type=['EU', 'USM', 'USW']`.
-   **Atomic Summary**: Provides a detailed report after upload (Rows skipped, colors updated, local-only flags triggered).

### 4.2 Checkout & Stock Deduction
Stock integrity is maintained via a strict post-payment lifecycle in `Others/views.py`:
-   **Trigger**: Stripe Webhook (`payment_intent.succeeded`).
-   **Concurrency Protection**: Uses **`F-expressions`** for atomic subtraction.
-   **Logic**:
    ```python
    PartnerProductSize.objects.filter(id=order.size.id).update(quantity=F('quantity') - order.quantity)
    ```
-   **Finance Integration**: Simultaneously calculates `net_amount` (Gross - Partner Fees - Other Charges) and updates the Partner's `Finance` balance.

---

## 5. Smart Inventory Intelligence (Alerts)

The `DashboardAPIView` provides proactive warehouse management via four specialized algorithms:

### 5.1 Low Stock Alerts
- **Simple Threshold**: Triggered when `total_stock_quantity <= 10`.
- **Purpose**: Immediate restocking notice for low-volume items.

### 5.2 Best-Selling Low Stock (Velocity-Based)
- **Algorithm**: Correlates sales data from the last 30 days with current stock.
- **Threshold**: Triggered when a top-selling product (Top 10) falls below 20 pairs.
- **Smart Message**: *"High demand detected. Recommended reorder: 15–20 pairs."* (Localized in DE/IT).

### 5.3 Inactive Product Optimizer
- Scans for `PartnerProduct` items that have **positive stock** but are set to `is_active=False`.
- Alerts partners to "activate" dormant inventory.

### 5.4 Seasonal Forecasting
- Maps current month to seasonal categories (e.g., Spring = Running/Hiking).
- Recommends marketing actions if a partner has high stock in relevant subcategories.

---

## 6. Storage & Accessories

### 6.1 Logical Warehousing
- Partners can define multiple `Warehouse` entries.
- Each `PartnerProduct` can be linked to a warehouse, allowing for location-based stock reports and logistics planning.

### 6.2 Accessories Management
- Non-shoe inventory (laces, sprays, socks) is managed via the `Accessories` model.
- Uses a simplified `stock` integer field rather than the complex size-table logic used for footwear.

---
*Created on 2026-02-03 | Comprehensive Stock documentation for Feet First Engineering*
