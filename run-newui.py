import sys
from do3se.ui import main
from do3se import model

setattr(model.parameters, 'h', 12.3)

main(sys.argv[1:])
