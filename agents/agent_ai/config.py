# Path to the file where wallet data is persisted
wallet_data_file = "wallet_data.txt"
# Agent LLM model
model = "gpt-4o-mini"
# Prusa slicer path
prusa_slicer_path = "/home/luka/PrusaSlicer/build/src/prusa-slicer"
# Prusa settings
prusa_settings = (
    "--slice "
    "--printer-profile=Prusa_MMU2S "
    "--material-profile=PLA --material-profile=ABS "
    "--extrusion-multiplier=1.05 "
)
