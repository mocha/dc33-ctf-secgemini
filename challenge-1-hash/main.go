package main

import (
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"fmt"
	"log"
	"os"
)

type Account struct {
	Id      uint16
	Balance uint64
}

var (
	Accounts []Account
	BankKey  []byte
)

func setup_bank_secret_key() {
	BankKey = make([]byte, 16)
	_, err := rand.Read(BankKey)

	if err != nil {
		log.Fatalf("err: %v\n", err)
	}
}

func setup_existing_accounts() {
	Accounts = append(Accounts, Account{
		Id:      1,
		Balance: 1000000000,
	})
}

func account_menu() {
	fmt.Println("1) check current balance")
	fmt.Println("2) create transaction")
	fmt.Println("3) execute transaction")
	fmt.Println("4) log out")
}

func check_current_balance(account *Account) {
	fmt.Printf("balance: %v\n", account.Balance)

	if account.Balance == 13371337 {
		flag, err := os.ReadFile("flag")
		if err != nil {
			log.Fatalf("err: %v\n", err)
		}

		fmt.Printf("%s\n", flag)
	}
}

func create_transaction(account *Account) {
	fmt.Println("please enter the account id you wish to send money to")

	var toId uint16
	_, err := fmt.Scanf("%d", &toId)

	if err != nil {
		log.Fatalf("err: %v\n", err)
	}

	fmt.Println("please enter the amount you wish to transfer")

	var amount uint64
	_, err = fmt.Scanf("%d", &amount)

	if err != nil {
		log.Fatalf("err: %v\n", err)
	}

	h := hmac.New(sha256.New, BankKey)
	h.Write([]byte(fmt.Sprintf("%d", account.Id)))
	h.Write([]byte(fmt.Sprintf("%d", toId)))
	h.Write([]byte(fmt.Sprintf("%d", amount)))
	mac := h.Sum(nil)

	fmt.Printf("authorization code: %x\n", mac)
}

func execute_transaction() {
	fmt.Println("please enter the account id you wish to send money from")

	var fromId uint16
	_, err := fmt.Scanf("%d", &fromId)

	if err != nil {
		log.Fatalf("err: %v\n", err)
	}

	var fromAccount *Account
	for idx, account := range Accounts {
		if account.Id == fromId {
			fromAccount = &Accounts[idx]
		}
	}

	if fromAccount == nil {
		fmt.Println("sorry, no such account exists")
		return
	}

	fmt.Println("please enter the account id you wish to send money to")

	var toId uint16
	_, err = fmt.Scanf("%d", &toId)

	if err != nil {
		log.Fatalf("err: %v\n", err)
	}

	var toAccount *Account
	for idx, account := range Accounts {
		if account.Id == toId {
			toAccount = &Accounts[idx]
		}
	}

	if toAccount == nil {
		fmt.Println("sorry, no such account exists")
		return
	}

	fmt.Println("please enter the amount you wish to transfer")

	var amount uint64
	_, err = fmt.Scanf("%d", &amount)

	if err != nil {
		log.Fatalf("err: %v\n", err)
	}

	if fromAccount.Balance < amount {
		fmt.Println("insufficient funds")
		return
	}

	h := hmac.New(sha256.New, BankKey)
	h.Write([]byte(fmt.Sprintf("%d", fromId)))
	h.Write([]byte(fmt.Sprintf("%d", toId)))
	h.Write([]byte(fmt.Sprintf("%d", amount)))
	expectedAuthCode := h.Sum(nil)

	fmt.Println("please enter the authorization code")

	var authCodeStr string
	_, err = fmt.Scanf("%s", &authCodeStr)

	if err != nil {
		log.Fatalf("err: %v\n", err)
	}

	authCode, err := hex.DecodeString(authCodeStr)

	if subtle.ConstantTimeCompare(authCode, expectedAuthCode) == 0 {
		fmt.Println("sorry, you are not authorized to make that transfer")
		return
	}

	fromAccount.Balance -= amount
	toAccount.Balance += amount

	fmt.Println("transaction completed")
}

func main_menu() {
	fmt.Println("1) create new account")
	fmt.Println("2) log in")
	fmt.Println("3) quit")
}

func create_new_account() {
	if len(Accounts) >= 100 {
		fmt.Println("sorry the bank cannot accommodate you at this time")
		return
	}

	fmt.Println("please provide your an unused account id to create a new account")

	var id uint16
	_, err := fmt.Scanf("%d", &id)

	if err != nil {
		log.Fatalf("err: %v\n", err)
	}

	for _, account := range Accounts {
		if account.Id == id {
			fmt.Printf("the account id %v is in use already\n", id)
			return
		}
	}

	Accounts = append(Accounts, Account{
		Id:      id,
		Balance: 0,
	})

	fmt.Printf("successfully created a new account with id %v\n", id)
}

func log_in() {
	fmt.Println("please provide your account id to log in")

	var id uint16
	_, err := fmt.Scanf("%d", &id)

	if err != nil {
		log.Fatalf("err: %v\n", err)
	}

	if id == 1 {
		fmt.Println("you cannot log into the account with this id")
		return
	}

	var currentAccount *Account
	for idx, account := range Accounts {
		if account.Id == id {
			currentAccount = &Accounts[idx]
		}
	}

	if currentAccount == nil {
		fmt.Println("sorry, this account doesn't exist")
		return
	}

	fmt.Printf("you are now logged into account %v\n", currentAccount.Id)

	for {
		account_menu()

		var choice int
		_, err := fmt.Scanf("%d", &choice)

		if err != nil {
			log.Fatalf("err: %v", err)
		}

		switch choice {
		case 1:
			{
				check_current_balance(currentAccount)
			}
		case 2:
			{
				create_transaction(currentAccount)
			}
		case 3:
			{
				execute_transaction()
			}
		case 4:
			{
				fmt.Println("you are logged out")
				return
			}
		default:
			{
				fmt.Printf("err: unknown choice %v\n", choice)
			}
		}
	}
}

func main() {
	setup_bank_secret_key()

	setup_existing_accounts()

	fmt.Println("welcome to the bank")

	for {
		main_menu()

		var choice int
		_, err := fmt.Scanf("%d", &choice)

		if err != nil {
			log.Fatalf("err: %v", err)
		}

		switch choice {
		case 1:
			{
				create_new_account()
			}
		case 2:
			{
				log_in()
			}
		case 3:
			{
				fmt.Println("thank you for using our service")
				return
			}
		default:
			{
				fmt.Printf("err: unknown choice %v\n", choice)
			}
		}
	}
}
