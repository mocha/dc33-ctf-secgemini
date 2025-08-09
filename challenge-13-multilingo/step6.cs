using System;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

class Program
{
    static void Main()
    {
        // Prompt the user for input
        Console.Write("Enter flag: ");
        string input = Console.ReadLine();

        // Validate input length
        if (input.Length < 29)
        {
            Environment.Exit(1);
        }

        int[][] specificCombinations = new int[][]
        {
            new int[] { 9, 11 },
            new int[] { 12, 14 },
            new int[] { 13, 15, 16 }
        };

        string[] expectedHashes = new string[]
        {
            "bd647713c2571a15f95b12b4e9e1a405a831d9c8c7abaf471095498fdb4c2160", 
            "ec7e008b5f4d05c43a532426d1d7b7cdb8e4452e3e29f9e4a1ad8833078a6907",
            "989c5f9a611ce3b7717a85ace23bd2c7e73ede567cb34bd5b754f955fcb603e2"
        };

        int passed = 0;

        for (int i = 0; i < specificCombinations.Length; i++)
        {
            string letters = new string(specificCombinations[i].Select(index => input[index]).ToArray());

            string hash = ComputeSHA256Hash(letters);

            if (hash == expectedHashes[i])
            {
                passed++;
            }
        }

        if (passed == specificCombinations.Length)
        {
            Environment.Exit(0);
        }
        else
        {
            Environment.Exit(1);
        }
    }

    static string ComputeSHA256Hash(string input)
    {
        using (SHA256 sha256 = SHA256.Create())
        {
            byte[] hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(input));
            return BitConverter.ToString(hashBytes).Replace("-", "").ToLower();
        }
    }
}
