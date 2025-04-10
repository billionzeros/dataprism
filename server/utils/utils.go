package utils

import (
	"strconv"
	"strings"
	"time"
)

// InferDataType takes a slice of strings and infers the data type based on the content of the strings.
func InferDataType(samples []string) string {
	isInt := true
	isFloat := true
	isBool := true
	isDate := true // Basic YYYY-MM-DD check

	// Common date layout to check
	const dateLayout = "2006-01-02"

	if len(samples) == 0 {
		return "string" // Default to string if no samples
	}

	for _, s := range samples {
		trimmed := strings.TrimSpace(s)
		if trimmed == "" {
			continue // Ignore empty strings for inference
		}

		// Check Integer
		if isInt {
			if _, err := strconv.ParseInt(trimmed, 10, 64); err != nil {
				isInt = false
			}
		}

		// Check Float (only if not already confirmed integer)
		if isFloat && !isInt {
			if _, err := strconv.ParseFloat(trimmed, 64); err != nil {
				isFloat = false
			}
		} else if !isInt { // If it wasn't an Int, it can't be a Float either based on ParseInt failing
            isFloat = false
        }


		// Check Boolean
		if isBool {
			lower := strings.ToLower(trimmed)
			if lower != "true" && lower != "false" && lower != "1" && lower != "0" && lower != "yes" && lower != "no" && lower != "t" && lower != "f" {
				isBool = false
			}
		}

		// Check Date (Basic YYYY-MM-DD)
		if isDate {
			if _, err := time.Parse(dateLayout, trimmed); err != nil {
				isDate = false
			}
		}
	}

	if isInt {
		return "integer"
	}
	if isFloat {
		return "float"
	}
	if isBool {
		return "boolean"
	}
	if isDate {
		return "date"
	}
	return "string"
}