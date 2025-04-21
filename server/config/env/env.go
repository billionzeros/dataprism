package env

import (
	"log"

	"github.com/spf13/viper"
)

type Env struct {
	// Run Time Creds
	Environment           string `mapstructure:"ENVIRONMENT"`

	// Gemini API Key
	GEMINI_API_KEY string `mapstructure:"GEMINI_API_KEY"`

	// Listen Address
	ListenAddr 		 string    `mapstructure:"LISTEN_ADDR"`

	// Axiom Creds
	AxiomToken   string `mapstructure:"AXIOM_TOKEN"`
	AxiomOrgID   string `mapstructure:"AXIOM_ORG_ID"`
	AxiomDataSet string `mapstructure:"AXIOM_DATASET"`

	// Database Creds
	DATABASE_URL string `mapstructure:"DATABASE_URL"`

	// AWS CREDS
	AWS_BUCKET_ENDPOINT string `mapstructure:"AWS_BUCKET_ENDPOINT"`
	AWS_BUCKET_ID	   string `mapstructure:"AWS_BUCKET_ID"`
	AWS_KEY_ID		string `mapstructure:"AWS_KEY_ID"`
	AWS_SECRET_KEY	 string `mapstructure:"AWS_SECRET_KEY"`
	AWS_BUCKET_NAME	 string `mapstructure:"AWS_BUCKET_NAME"`
	AWS_BUCKET_REGION string `mapstructure:"AWS_BUCKET_REGION"`
}

// LoadEnvironmentVariables loads environment variables
func LoadEnvironmentVariables(envFile string) (*Env, error) {
	viper.SetDefault("ENVIRONMENT", "development")
	viper.SetDefault("LISTEN_ADDR", "127.0.0.1:8080")

	env := &Env{}

	if envFile != "" {
		envFile = ".env"
	}

	viper.SetConfigFile(envFile)

	err := viper.ReadInConfig()
	if err != nil {
		return nil, err
	}

	err = viper.Unmarshal(&env)

	if err != nil {
		log.Fatal("Environment can't be loaded: ", err)
		return nil, err
	}

	return env, nil
}

// IsDevelopment returns true if the environment is development
func IsDevelopment() bool {
	return viper.GetString("ENVIRONMENT") == "development"
}

// GeminiAPIKey returns the Gemini API key which used for AI models from Google.
func GetGeminiAPIKey() string {
	return viper.GetString("GEMINI_API_KEY")
}

func GetAxiomToken() string {
	return viper.GetString("AXIOM_TOKEN")
}

func GetAxiomOrgID() string {
	return viper.GetString("AXIOM_ORG_ID")
}

func GetAxiomDataSet() string {
	return viper.GetString("AXIOM_DATASET")
}

func GetDatabaseURL() string {
	return viper.GetString("DATABASE_URL")
}

func GetListenAddr() string {
	return viper.GetString("LISTEN_ADDR")
}

type AWSBucketCreds struct {
	AWSBucketEndpoint string
	AWSBucketID       string
	AWSKeyID         string
	AWSSecretKey     string
	AWSBucketName    string
	AWSBucketRegion  string
}

func GetAWSBucketCreds() *AWSBucketCreds {
	return &AWSBucketCreds{
		AWSBucketEndpoint: viper.GetString("AWS_BUCKET_ENDPOINT"),
		AWSBucketID:       viper.GetString("AWS_BUCKET_ID"),
		AWSKeyID:         viper.GetString("AWS_KEY_ID"),
		AWSSecretKey:     viper.GetString("AWS_SECRET_KEY"),
		AWSBucketName:    viper.GetString("AWS_BUCKET_NAME"),
		AWSBucketRegion:  viper.GetString("AWS_BUCKET_REGION"),
	}
}