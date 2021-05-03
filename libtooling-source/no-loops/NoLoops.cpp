#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"

#include "llvm/Support/CommandLine.h"

using namespace clang::ast_matchers;
using namespace clang::tooling;
using namespace clang;
using namespace llvm;

class MyPrinter : public MatchFinder::MatchCallback {
 public:
  virtual void run(const MatchFinder::MatchResult &Result) {
    ASTContext *Context = Result.Context;
    // Ugly code: determines if code containing a statement is imporant, and returns its location and filename.
    if (const clang::Stmt *E =
            Result.Nodes.getNodeAs<clang::Stmt>("loops")) {
      FullSourceLoc FullLocation = Context->getFullLoc(E->getBeginLoc());
      if (FullLocation.isValid() && Context->getSourceManager().isInMainFile(FullLocation)) {
        llvm::outs() << "Found loop in file '" + Context->getSourceManager().getFilename(FullLocation) + "' at " << FullLocation.getSpellingLineNumber()
                     << ":" << FullLocation.getSpellingColumnNumber() << " \n";
      }
    }
  }
};

// Apply a custom category to all command-line options so that they are the
// only ones displayed.
static llvm::cl::OptionCategory NoLoopsCategory("no-loops options");

// CommonOptionsParser declares HelpMessage with a description of the common
// command-line options related to the compilation database and input files.
// It's nice to have this help message in all tools.
static cl::extrahelp CommonHelp(CommonOptionsParser::HelpMessage);

// A help message for this specific tool can be added afterwards.
// Stuff Things
static cl::extrahelp MoreHelp("\nMore help text...");

int main(int argc, const char **argv) {
  // Parse arguments.
  CommonOptionsParser OptionsParser(argc, argv, NoLoopsCategory);
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());

  // Initialize tools for finding specific statements.
  MyPrinter Printer;
  MatchFinder Finder;

  // Match statements of specific types.
  StatementMatcher forMatcher =
      forStmt().bind("loops");
	  
	StatementMatcher whileMatcher =
      whileStmt().bind("loops");

  // Prepare to compile and find them.
  Finder.addMatcher(forMatcher, &Printer);
  Finder.addMatcher(whileMatcher, &Printer);

  // Go
  return Tool.run(newFrontendActionFactory(&Finder).get());
}