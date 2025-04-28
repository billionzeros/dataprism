package responses

import (
	"net/http"

	"github.com/gofiber/fiber/v3"
)

// Standard API response
type APIResponse struct {
    Success bool        `json:"success"`
    Data    interface{} `json:"data,omitempty"`
    Error   *APIError   `json:"error,omitempty"`
}

// API error details
type APIError struct {
    Code    int `json:"code"`
    Message string `json:"message"`
}

// OK returns a successful `200`` response with data
func OK(c fiber.Ctx, data interface{}) error {
    return c.Status(http.StatusOK).JSON(APIResponse{
        Success: true,
        Data:    data,
    })
}

// Accepted returns a `202`` accepted response
func Accepted(c fiber.Ctx, data interface{}) error {
    return c.Status(http.StatusAccepted).JSON(APIResponse{
        Success: true,
        Data:    data,
    })
}



// Created returns a successful creation `201` response
func Created(c fiber.Ctx, data interface{}) error {
    return c.Status(http.StatusCreated).JSON(APIResponse{
        Success: true,
        Data:    data,
    })
}

// StatusMultiStatus returns a `207` multi-status response, meaning some submissions failed
func StatusMultiStatus(c fiber.Ctx, data interface{}) error {
    return c.Status(http.StatusMultiStatus).JSON(APIResponse{
        Success: true,
        Data:    data,
    })
}

// BadRequest returns a `400` bad request error
func BadRequest(c fiber.Ctx, code int, message string) error {
    return c.Status(http.StatusBadRequest).JSON(APIResponse{
        Success: false,
        Error: &APIError{
            Code:    code,
            Message: message,
        },
    })
}

// NotFound returns a 404 not found error
func NotFound(c fiber.Ctx, code int, message string) error {
    return c.Status(http.StatusNotFound).JSON(APIResponse{
        Success: false,
        Error: &APIError{
            Code:    code,
            Message: message,
        },
    })
}