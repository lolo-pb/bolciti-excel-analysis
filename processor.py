from modules.sueldos import build_sueldos_by_section, build_sueldos_by_employee
from modules.gastos import build

###  Esto deberia llamar a los modules y cada module deberia devolver las 
### tablas divididas por mes/ o dividirlas en el main?
def main():
        #sueldos = build_sueldos_by_section()
        #print(sueldos.to_string(index=False))

        gastos = build()
        print(gastos.to_string(index=False))

if __name__ == "__main__":
    main()
