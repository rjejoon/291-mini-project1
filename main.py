


def main():
    
    run = True
    while run:
        
        # first screen
        uInput = input("Options: (si) sign in, (su) sign up, (q)uit: ").lower()

        if uInput == 'q':
            run = False
        elif uInput == 'si':
            signIn()
        elif uInput == 'su':
            signUp()

        else:
            print("error: command not found.")



if __name__ == "__main__":

    main()
