\# Lab 5: Static Code Analysis — Reflection



\## 1. What is static code analysis?



Static code analysis examines source code without executing it. In this lab, Pylint checked code quality, Bandit identified potentially insecure coding patterns, and Flake8 checked Python formatting and style.



\## 2. What issues did you identify and fix?



I addressed security and logic issues, including disabled HTTPS certificate verification, a missing HTTP timeout, unsafe shell-based backup commands, an outdated TLS configuration, a hardcoded API key, a mutable default argument, and division by zero when attendance records are empty. I also fixed formatting issues reported by Flake8.



\## 3. How did the tools help improve the program?



Bandit reported zero issues after the fixes. Flake8 produced an empty after-report, indicating no remaining reported style issues. Pylint reached 10.00/10 when the C0103 naming-style warning was disabled to preserve the original function names.



\## 4. What did you learn from this lab?



I learned that static analysis tools identify different classes of problems and complement one another. Security findings should be prioritized, and the program should be tested after changes to ensure that its behavior remains correct. I also learned to save before-and-after reports to document the improvement.



