"""
Security and Bug Report for Feetfirst Project
=============================================

This report identifies potential security vulnerabilities and bugs in the project.
Each issue is categorized by severity and includes recommendations for remediation.
"""

# Security Issues
SECURITY_ISSUES = [
    {
        "title": "Wildcard Imports",
        "severity": "Medium",
        "location": "views.py",
        "description": "Using wildcard imports (from .utils import *) makes code less readable and can introduce "
                      "namespace conflicts. It's also harder to track which functions are being used.",
        "recommendation": "Replace wildcard imports with explicit imports of only the needed functions/classes."
    },
    {
        "title": "Missing CSRF Protection",
        "severity": "High",
        "location": "SocialAuthCallbackView",
        "description": "The API views don't explicitly use CSRF protection which could expose endpoints to CSRF attacks.",
        "recommendation": "Ensure CSRF protection is properly implemented for all state-changing operations."
    },
    {
        "title": "Insecure Direct Object Reference",
        "severity": "High",
        "location": "AddressDetailView",
        "description": "The queryset filtering happens after object retrieval which could potentially allow "
                      "access to other users' addresses if not properly implemented.",
        "recommendation": "Ensure proper object-level permissions are checked before any data is returned."
    },
    {
        "title": "Error Handling Exposes Information",
        "severity": "Medium",
        "location": "SocialAuthCallbackView",
        "description": "The exception handler returns the raw error message which might expose sensitive information.",
        "recommendation": "Use generic error messages and log the actual errors server-side."
    },
    {
        "title": "Token Verification Vulnerability",
        "severity": "High",
        "location": "SocialAuthCallbackView",
        "description": "The access token is passed directly in the URL for verification which could expose it in logs.",
        "recommendation": "Use POST parameters or headers for token verification instead of query parameters."
    },
]

# Bug Issues
BUG_ISSUES = [
    {
        "title": "Missing queryset in AddressListCreateView",
        "severity": "High",
        "location": "AddressListCreateView.get_queryset",
        "description": "The get_queryset method references self.queryset but no queryset is defined on the class.",
        "recommendation": "Define queryset = Address.objects.all() on the class."
    },
    {
        "title": "Inconsistent HTTP Status Codes",
        "severity": "Low",
        "location": "Multiple views",
        "description": "Some views use status.HTTP_400_BAD_REQUEST while others use numeric 400. "
                      "This inconsistency can make error handling more difficult.",
        "recommendation": "Consistently use status constants from rest_framework.status."
    },
    {
        "title": "Missing settings Import",
        "severity": "Medium",
        "location": "views.py",
        "description": "The code references settings but doesn't import it.",
        "recommendation": "Add 'from django.conf import settings' to the imports."
    },
    {
        "title": "Unused Variable",
        "severity": "Low",
        "location": "SocialAuthCallbackView",
        "description": "The phone variable is retrieved but never used.",
        "recommendation": "Remove unused variables to improve code clarity."
    },
    {
        "title": "Missing Status Code in Response",
        "severity": "Low",
        "location": "SocialAuthCallbackView.post",
        "description": "The successful response doesn't specify a status code.",
        "recommendation": "Add status=status.HTTP_200_OK to the Response."
    },
]

# Performance Issues
PERFORMANCE_ISSUES = [
    {
        "title": "Multiple Database Queries",
        "severity": "Medium",
        "location": "SocialAuthCallbackView",
        "description": "The view makes multiple database queries which could be optimized.",
        "recommendation": "Consider using select_related or prefetch_related to reduce database queries."
    },
    {
        "title": "Synchronous HTTP Requests",
        "severity": "Medium",
        "location": "SocialAuthCallbackView",
        "description": "The view makes synchronous HTTP requests which could block the server.",
        "recommendation": "Consider using asynchronous requests or background tasks for HTTP calls."
    },
]

# Best Practice Issues
BEST_PRACTICE_ISSUES = [
    {
        "title": "Missing Docstrings",
        "severity": "Low",
        "location": "All views",
        "description": "Classes and methods lack docstrings which makes the code harder to understand.",
        "recommendation": "Add docstrings to all classes and methods."
    },
    {
        "title": "Inconsistent Naming",
        "severity": "Low",
        "location": "Multiple views",
        "description": "Variable naming is inconsistent (e.g., serializers vs serializer).",
        "recommendation": "Use consistent naming throughout the codebase."
    },
    {
        "title": "Non-English Comments",
        "severity": "Low",
        "location": "SocialAuthCallbackView",
        "description": "Comments in non-English can make code maintenance difficult for teams with diverse backgrounds.",
        "recommendation": "Use English for all code comments for better maintainability."
    },
]

def generate_report():
    """Generate a formatted report of all issues."""
    all_issues = []
    all_issues.extend([("SECURITY", issue) for issue in SECURITY_ISSUES])
    all_issues.extend([("BUG", issue) for issue in BUG_ISSUES])
    all_issues.extend([("PERFORMANCE", issue) for issue in PERFORMANCE_ISSUES])
    all_issues.extend([("BEST PRACTICE", issue) for issue in BEST_PRACTICE_ISSUES])
    
    # Sort by severity
    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    all_issues.sort(key=lambda x: severity_order.get(x[1]["severity"], 3))
    
    report = "# Security and Bug Report for Feetfirst Project\n\n"
    
    for category, issue in all_issues:
        report += f"## [{category}] {issue['title']} - {issue['severity']}\n"
        report += f"**Location:** {issue['location']}\n\n"
        report += f"**Description:** {issue['description']}\n\n"
        report += f"**Recommendation:** {issue['recommendation']}\n\n"
        report += "---\n\n"
    
    return report

if __name__ == "__main__":
    print(generate_report())