# WebCat-Clang 
WebCat plugin for grading C++ code using LLVM and Clang.

# Why Clang / Overview of the issues

Since WebCat’s introduction, its primary C++ plugin has used G++. This remained true for CXL, the current WebCat plugin used for C++ grading at QCC designed to improve the style grading of the original plugin. With advancements in Clang (G++ main competitor) and LLVM, specifically with the improvements in its AST (Abstract Syntax Tree) with the introduction of Clang Libtooling, as well as other improvements to its code coverage functions (which are needed as CXL’s code coverage check is currently broken), have made it a prime candidate for use in more advanced grading systems. Many early programming projects require manual assistance from the professor because assignments parameters such as “no loops” (for teaching recursion) or “no array indexing”(for teaching pointer arithmetic). With Clang Libtooling it is trivially easy to create tools to implement these rules, allowing previously manual tasks to be left to the grader. Other important features of the grader can be reimplemented using Clang and LLVM, so no functionality is lost.

# Features

Error Transparent: One of the big problems with CXL was the lack of a report of certain errors to the student. Now all errors are printed to the student to help them determine where the error is coming from.

Code Coverage: Major improvements to the usability and visibility of code coverage. Now fully customizable and using LLVM-COV as a backend, it displays everything to the student. All code in the student's submission must be covered or they will get a 0 for that portion of the grade.

Python Picks Up the Pace: Using python instead of perl, the grading time has easily cut in half. Students don't have to wait as long for their results.

# Settings

 * Plugin Settings (For all assignments of a type):

General Includes and Libraries
- Adds generic includes and libraries to the compiling of all assignments

C++ Version
- Options are 98, 11, and 14.

* Assignment Settings (Per Assignment Options):

Instructor Tests
- Test files to run along side the students.

Minimum Students Tests
- A set minimum that lowers a students grade if they do not hit it.

All Student Tests Must Pass
- Grants a zero if a student's tests do not all pass.

Code Coverage
- Enables code coverage grading.

Code Coverage Options
- There are a few. Enable and disable parts of the code coverage data from being considered.

Data Files
- Add files into the program directory that are required by the program.

Extra Include Directory
- Similar to the plugin setting but for the assignment.

Extra Linking Library
- Similar to the plugin setting but for the assignment.

No Loops Check (Designed for recursion homework)
- Clang Libtooling Implementation. Check that detects loops and gives a zero should it find any.

No Array Indexing Check (Designed for pointer arithmetic homework)
- Clang Libtooling Implementation. Check that detects array indexing and gives a zero should it find any.


# Installation Instructions

Add ZIP to WebCAT as you would a normal plugin. Then run the install script through the console. The installation script and some feature only work on Ubuntu at the moment as it uses apt as the package manager.

If on other hardware, make sure LLVM-8 and Clang-8 are installed and added to path.

Plugin located at WebCAT's storage directory. In testing on Ubuntu 16 it was /usr/share/Web-CAT

# Tested On

* Ubuntu 16 (Digital Ocean as Host)

# Change Log
Ver 1.0
Initial Release: CXL Plug-In for fully automated student code grading (Thomas Graham).

Ver 1.1
First implementation of Clang still on Perl language.

Ver 1.1.2
Full transition to python as the main  language of the plugin .

Ver 1.2
Implementation of extra features such as: admin test output, no loops checker and no indexing.

Ver 1.2.2
Added number of min test cases feature, code coverage implementation and style grading.

Ver 1.3 (Current)
Implemented any extra niche features, execution time greatly reduced (15 sec --> 3 sec processing time)
