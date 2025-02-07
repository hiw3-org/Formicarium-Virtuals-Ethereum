# Path to the file where wallet data is persisted
wallet_data_file = "wallet_data.txt"
# Agent LLM model
model = "gpt-4o-mini"
# Prusa slicer path
prusa_slicer_path = "/home/luka/PrusaSlicer/build/src/prusa-slicer"
# Prusa settings
# prusa_settings = (
#     "--slice "
#     "--load agents/keychain_design/PrusaSlicer_config_bundle.ini "  # Global settings
# )
prusa_settings = (
    "--slice "
    "--load agents/keychain_design/MMU_PLA.ini "  # Fillament settings
    "--load agents/keychain_design/MMU2S_Preset.ini "  # Printer settings
    "--layer-height 0.20 " 
)

#---------> Blockchain tools <---------
# Network ID
NETWORK_ID = "base-sepolia"
# Formicarium smart contract address
FORMICARIUM_SC_ADDRESS = "0xE2BBceBC540bEF2e1d76dD3154Bd94Bf1846b705"
# ERC20 contract address
ERC20_TOKEN_ADDRESS = "0x3207249ba95035b067D9700A5d221531A6eA3BcB"
