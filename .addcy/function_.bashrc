# Agregar al final de .bashrc

addcy () {
    PYTHON_SCRIPT="$HOME/.addcy/addcy.py"
    python3 "$PYTHON_SCRIPT" "$1"
}
