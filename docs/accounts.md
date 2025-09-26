# Accounts Application

This document details the `Accounts` application, which manages user authentication, profiles, and related functionalities.

## Models

- **User**: [Description of the User model fields and its purpose]
- **AccountDeletionRequest**: [Description of the AccountDeletionRequest model fields and its purpose]
- **OTP**: [Description of the OTP model fields and its purpose]
- **Address**: [Description of the Address model fields and its purpose]

## Views

[Description of views in the Accounts app, their functionalities, and associated URLs.]

## Serializers

[Description of serializers used in the Accounts app for API data representation.]

## Admin Panel Configuration

This section describes the customizations made to the Django admin interface for the `Accounts` application.

### UserAdmin

- **`list_display`**: Fields displayed in the list view.
- **`list_filter`**: Fields available for filtering.
- **`search_fields`**: Fields searchable in the admin.
- **`readonly_fields`**: Fields that are read-only.
- **`fieldsets`**: Grouping of fields in the detail view.
- **`get_queryset`**: Custom queryset for row-level permissions.
- **`has_change_permission`**: Custom logic for change permissions.
- **`has_delete_permission`**: Custom logic for delete permissions.
- **`get_fieldsets`**: Custom fieldsets based on user role.
- **`get_readonly_fields`**: Custom read-only fields based on user role.

### DeleteAdmin

- **`list_display`**: Fields displayed in the list view.
- **`readonly_fields`**: Fields that are read-only.
- **`fields`**: Fields displayed in the detail view.
- **`search_fields`**: Fields searchable in the admin.
- **`formatted_reason`**: Custom method to display deletion reasons.
- **`has_add_permission`**: Disables the add button.

### OtpAdmin

- **`list_display`**: Fields displayed in the list view.
- **`search_fields`**: Fields searchable in the admin.
- **`list_filter`**: Fields available for filtering.
- **`readonly_fields`**: Fields that are read-only.
- **`has_add_permission`**: Disables the add button.

### SurvayAdmin

- **`list_display`**: Fields displayed in the list view.
- **`readonly_fields`**: Fields that are read-only.
- **`fields`**: Fields displayed in the detail view.
- **`search_fields`**: Fields searchable in the admin.
- **`list_filter`**: Fields available for filtering.
- **`formatted_discovery_question`**: Custom method to display discovery questions.
- **`truncated_foot_problems`**: Custom method to truncate foot problems.

### AddressAdmin

- **`list_display`**: Fields displayed in the list view.
- **`list_filter`**: Fields available for filtering.
- **`search_fields`**: Fields searchable in the admin.
- **`ordering`**: Default ordering for the list view.
- **`readonly_fields`**: Fields that are read-only.