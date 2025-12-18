from modules.sueldos import build_sueldos_by_section, build_sueldos_by_employee

###  Esto deberia llamar a los modules y cada module deberia devolver las 
### tablas divididas por mes/ o dividirlas en el main?
def main():
        sueldos = build_sueldos_by_section()
        print(sueldos.to_string(index=False))

if __name__ == "__main__":
    main()
