package appError

type appError struct {
	code    int
	message string
	err     error
}

type AppError interface {
	Error() string
	Unwrap() error
	Code() int
}

// NewAppError creates a new AppError
func New(code int, message string, err error) AppError {
	return &appError{
		message: message,
		code:    code,
		err:     err,
	}
}

// Error returns the error message
func (e *appError) Error() string {
	return e.message
}

// Unwrap returns the wrapped error
func (e *appError) Unwrap() error {
	return e.err
}

// Code returns the error code
func (e *appError) Code() int {
	return e.code
}

const (
	// BadRequest indicates the request was malformed or invalid
	BadRequest = 400
	// Unauthorized indicates authentication is required
	Unauthorized = 401
	// Forbidden indicates the request was valid but the server refuses action
	Forbidden = 403
	// NotFound indicates the requested resource does not exist
	NotFound = 404
	// MethodNotAllowed indicates the request method is not supported
	MethodNotAllowed = 405
	// Conflict indicates a conflict with the current state of the resource
	Conflict = 409
	// Timeout indicates the request timed out
	Timeout = 408
	// TooManyRequests indicates the user has sent too many requests
	TooManyRequests = 429
)

// Server Error Codes (5xx)
const (
	// InternalError indicates an unexpected server error
	InternalError = 500
	// NotImplemented indicates the server does not support the functionality
	NotImplemented = 501
	// ServiceUnavailable indicates the server is temporarily unavailable
	ServiceUnavailable = 503
	// GatewayTimeout indicates upstream service timeout
	GatewayTimeout = 504
)

// Custom Application Error Codes (1xxx)
const (
	// ValidationError indicates data validation failure
	ValidationError = 1001
	// DatabaseError indicates database operation failure
	DatabaseError = 1002
	// CacheError indicates cache operation failure
	CacheError = 1003
	// ExternalServiceError indicates third-party service failure
	ExternalServiceError = 1004
	// InvalidInput indicates invalid input
	InvalidInput = 1005
)
