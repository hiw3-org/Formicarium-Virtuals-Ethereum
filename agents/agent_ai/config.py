# Path to the file where wallet data is persisted
wallet_data_file = "wallet_data.txt"
# Agent LLM model
model = "gpt-4o-mini"
# Dalle model
dalle_model = "dall-e-2"
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
