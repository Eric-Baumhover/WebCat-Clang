# WebCat-Clang
WebCat plugin for grading C++ code, requires a cxxtest-4.4 directory placed within to work.

# Why Clang / Overview of the issues

Since WebCat’s introduction, its primary C++ plugin has used G++. This remained true for CXL, the current WebCat plugin used for C++ grading at QCC designed to improve the style grading of the original plugin. With advancements in Clang (G++ main competitor) and LLVM, specifically with the improvements in its AST (Abstract Syntax Tree) with the introduction of Clang Libtooling, as well as other improvements to its code coverage functions (which are needed as CXL’s code coverage check is currently broken), have made it a prime candidate for use in more advanced grading systems. Many early programming projects require manual assistance from the professor because assignments parameters such as “no loops” (for teaching recursion) or “no array indexing”(for teaching pointer arithmetic). With Clang Libtooling it is trivially easy to create tools to implement these rules, allowing previously manual tasks to be left to the grader. Other important features of the grader can be reimplemented using Clang and LLVM, so no functionality is lost.

# Installation Instructions






# Change Log
Ver 1.0
Initial Release: CXL Plug-In for fully automated student code grading (Thomas Graham).

Ver 1.1
First implementation of Clang still on Perl language.

Ver 1.1.2
Full transition to python as the main plugin for WebCat.

Ver 1.2
Implementation of extra features such as: admin test output, no loops checker and no indexing.

Ver 1.2.2
Added number of min test cases feature, code coverage implementation and style grading.

Ver 1.3 (Current)
Implemented any extra niche features, execution time greatly increased (15 sec to 3 sec processing time)
