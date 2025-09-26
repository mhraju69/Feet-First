# Products Application

This document details the `Products` application, which manages product information, categories, and related functionalities.

## Models

- **Product**: [Description of the Product model fields and its purpose]
- **Category**: [Description of the Category model fields and its purpose]
- **Color**: [Description of the Color model fields and its purpose]
- **Size**: [Description of the Size model fields and its purpose]
- **ProductImage**: [Description of the ProductImage model fields and its purpose]
- **FootScan**: [Description of the FootScan model fields and its purpose]

## Views

[Description of views in the Products app, their functionalities, and associated URLs.]

## Serializers

[Description of serializers used in the Products app for API data representation.]

## Admin Panel Configuration

This section describes the customizations made to the Django admin interface for the `Products` application.

### ColorAdmin

- **`list_display`**: Fields displayed in the list view.
- **`search_fields`**: Fields searchable in the admin.

### ProductImageInline

- **`model`**: Associated model.
- **`extra`**: Number of empty forms.
- **`fields`**: Fields displayed in the inline form.

### SizeInline

- **`model`**: Associated model.
- **`extra`**: Number of empty forms.

### ProductQuestionAnswerInline

- **`model`**: Associated model.
- **`extra`**: Number of empty forms.
- **`autocomplete_fields`**: Fields with autocomplete functionality.

### SizeTableAdmin

- **`list_display`**: Fields displayed in the list view.
- **`search_fields`**: Fields searchable in the admin.
- **`inlines`**: Inline forms included.

### ProductAdmin

- **`list_display`**: Fields displayed in the list view.
- **`search_fields`**: Fields searchable in the admin.
- **`list_filter`**: Fields available for filtering.
- **`autocomplete_fields`**: Fields with autocomplete functionality.
- **`inlines`**: Inline forms included.
- **`get_queryset`**: Custom queryset for row-level permissions.
- **`has_change_permission`**: Custom logic for change permissions.
- **`has_delete_permission`**: Custom logic for delete permissions.
- **`has_view_permission`**: Custom logic for view permissions.
- **`save_model`**: Custom logic for saving the model, including assigning partners.
- **`formfield_for_foreignkey`**: Custom logic for foreign key form fields, especially for the 'partner' field.

### FootScanAdmin

- **`ModelAdmin`**: Default ModelAdmin configuration.