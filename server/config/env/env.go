package env

import (
	"log"

	"github.com/spf13/viper"
)

type Env struct {
	// Run Time Creds
	Environment           string `mapstructure:"ENVIRONMENT"`

	// Axiom Creds
	AxiomToken   string `mapstructure:"AXIOM_TOKEN"`
	AxiomOrgID   string `mapstructure:"AXIOM_ORG_ID"`
	AxiomDataSet string `mapstructure:"AXIOM_DATASET"`

	// Database Creds
	DATABASE_URL string `mapstructure:"DATABASE_URL"`
}

// LoadEnvironmentVariables loads environment variables
func LoadEnvironmentVariables(envFile string) (*Env, error) {
	viper.SetDefault("ENVIRONMENT", "development")
	viper.SetDefault("INSTANCE_ID", 1337)
	viper.SetDefault("RPC_PORT", 8700)
	viper.SetDefault("API_PORT", 8600)
	viper.SetDefault("BADGER_PORT", 8800)
	viper.SetDefault("ENABLE_QOS_PROTOCOL", false)
	viper.SetDefault("METRICS_PORT", 8900)

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

func GetBootstrappingNodeAddr() string {
	return viper.GetString("BOOTSTRAPPING_NODE_ADDR")
}

func EnableQOSProtocol() bool {
	return viper.GetBool("ENABLE_QOS_PROTOCOL")
}

func EnablePingProtocol() bool {
	return viper.GetBool("ENABLE_PING_PROTOCOL")
}

func GetPoolManagerContractAddr() string {
	return viper.GetString("POOL_MANAGER_CONTRACT_ADDR")
}

func GetBootstrapRewardContractAddr() string {
	return viper.GetString("BOOTSTRAP_REWARD_CONTRACT_ADDR")
}

func GetRewardsCalculatorContractAddr() string {
	return viper.GetString("REWARDS_CALCULATOR_CONTRACT_ADDR")
}

func CheckDelegation() bool {
	val := viper.GetString("RPC_URL")
	return val != ""
}

func GetPrometheusPort() int {
	return viper.GetInt("METRICS_PORT")
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

func GetProofOfResouceAddress() string {
	return viper.GetString("PROOF_OF_RESOURCE_CONTRACT_ADDR")
}

func GetRegistryPrivateKey() string {
	return viper.GetString("REGISTRY_PRIVATE_KEY")
}

func GetHudlChainId() int64 {
	return viper.GetInt64("HUDDLE_CHAIN_ID")
}

func GetHudlRPCURL() string {
	return viper.GetString("HUDDLE_RPC_URL")
}

func GetAdminApiKey() string {
	return viper.GetString("ADMIN_API_KEY")
}
