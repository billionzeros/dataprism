package chatService

type ChatRole string

const (
	// UserRole represents the user role in the chat.
	UserRole ChatRole = "user"

	// AssistantRole represents the assistant role in the chat.
	AssistantRole ChatRole = "assistant"

	// SystemRole represents the system role in the chat.
	SystemRole ChatRole = "system"

	// ToolRole represents the tool role in the chat.
	ToolRole ChatRole = "tool"
)

// CreateNewChat represents the request to create a new chat.
type CreateNewChat struct {
	// WorkspaceId is the ID of the workspace associated with the chat.
	WorkspaceId string `json:"workspace_id"`

	// BlockId is the ID of the block associated with the chat.
	BlockId string `json:"block_id"`
}

// ChatMessage represents a message in the chat.
type ChatMessage struct {
	// ChatId is the unique identifier for the Message ( which contains all the user queries.)
	ChatId string `json:"chat_id"`

	// MessageId is the unique identifier for the message.
	MessageId string `json:"message_id"`

	// Message is the content of the chat message.
	Message string `json:"message"`

	// Role is the role of the sender (e.g., "user", "assistant", "system").
	Role ChatRole `json:"role"`

	// Timestamp is the time when the message was sent.
	Timestamp string `json:"timestamp"`
}

// ChatDetails represents the details of a chat, contains all the messages exchanged in the chat.
type ChatDetails struct {
	// DocumentID is the unique identifier for the document.
	DocumentID string `json:"document_id"`

	// ChatID is the unique identifier for the chat ( which contains all the user queries.)
	ChatID string `json:"chat_id"`

	// Message is the content of the chat message.
	Messages []ChatMessage `json:"messages"`

	// Timestamp is the time when the message was sent.
	Timestamp string `json:"timestamp"`

	// Status is the status of the chat (e.g., "active", "completed").
	Status string `json:"status"`
}