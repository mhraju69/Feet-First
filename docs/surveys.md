# Surveys Application

This document details the `Surveys` application, which manages user surveys and their responses.

## Models

- **OnboardingSurvey**: [Description of the OnboardingSurvey model fields and its purpose]

## Views

[Description of views in the Surveys app, their functionalities, and associated URLs.]

## Serializers

[Description of serializers used in the Surveys app for API data representation.]

## Admin Panel Configuration

This section describes the customizations made to the Django admin interface for the `Surveys` application.

### SurvayAdmin

- **`list_display`**: Fields displayed in the list view.
- **`readonly_fields`**: Fields that are read-only.
- **`fields`**: Fields displayed in the detail view.
- **`search_fields`**: Fields searchable in the admin.
- **`list_filter`**: Fields available for filtering.
- **`formatted_discovery_question`**: Custom method to display discovery questions as badges.
- **`formatted_interests`**: Custom method to display interests as badges.
- **`truncated_foot_problems`**: Custom method to truncate foot problems for display.
- **`has_add_permission`**: Disables the add button.