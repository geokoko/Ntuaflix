def get_custom_responses():
    return {
        204: {
            "description": "No content found",
            "content": {
                "application/json": {
                    "example": {"detail": "No content found"}
                }
            }
        },
        400: {
            "description": "Bad request, unsupported format specified",
            "content": {
                "application/json": {
                    "example": {"detail": "Unsupported format specifier"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "An unexpected error occurred"}
                }
            }
        },
    }