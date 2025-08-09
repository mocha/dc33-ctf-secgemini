package main

import (
	"fmt"
)

var (
	Gor1Qq = func() [] /*line :1*/ byte {
		seed := /*line :1*/ byte(82)
		var data []byte
		type decFunc func(byte) decFunc
		var fnc decFunc
		fnc = func(x byte) decFunc { data = /*line :1*/ append(data, x-seed); seed += x; return fnc }
		/*line :1*/ fnc(83)(187)(100)(253)(232)(189)(215)(105)(195)(158)(17)(137)(205)(139)(47)(82)(237)(147)(255)(10)(32)(70)(121)(233)(232)(184)(225)(124)(232)(35)(250)(211)(189)(152)(103)(147)(12)(28)(141)(208)(145)(22)(81)(223)(121)(210)(179)(96)(213)(132)(115)(165)(43)(123)(54)(34)(30)(83)(159)(82)(235)(148)(92)(148)
		return data
	}()
)

func main() {
	var qvs_A0G2 string
	/*line :1*/ fmt.Scanf("%s", &qvs_A0G2)

	if /*line :1*/ len(qvs_A0G2) != /*line :1*/ len(Gor1Qq) {
		/*line :1*/ fmt.Println("nope")
		return
	}

	hCpJMrK := [] /*line :1*/ byte(qvs_A0G2)

	for jKmdi4d, i2JN2uuak := range hCpJMrK {
		hCpJMrK[jKmdi4d] = i2JN2uuak ^ 0x42
	}

	for jKmdi4d, i2JN2uuak := range hCpJMrK {
		if Gor1Qq[jKmdi4d] != i2JN2uuak {
			/*line :1*/ fmt.Println("nope.")
			return
		}
	}

	/*line :1*/
	fmt.Println(func() /*line :1*/ string {
		seed := /*line :1*/ byte(101)
		var data []byte
		type decFunc func(byte) decFunc
		var fnc decFunc
		fnc = func(x byte) decFunc { data = /*line :1*/ append(data, x-seed); seed += x; return fnc }
		/*line :1*/ fnc(200)(156)(59)(118)(223)(188)(137)(191)
		return /*line :1*/ string(data)
	}())
}
