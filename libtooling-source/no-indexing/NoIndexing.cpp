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
    if (const clang::Stmt *E =
            Result.Nodes.getNodeAs<clang::Stmt>("operation")) {
      FullSourceLoc FullLocation = Context->getFullLoc(E->getBeginLoc());
      if (FullLocation.isValid() && Context->getSourceManager().isInMainFile(FullLocation)) {
        llvm::outs() << "Found array index operation in file '" + Context->getSourceManager().getFilename(FullLocation) + "' at " << FullLocation.getSpellingLineNumber()
                     << ":" << FullLocation.getSpellingColumnNumber() << " \n";
      }
    }
  }
};

// Apply a custom category to all command-line options so that they are the
// only ones displayed.
static llvm::cl::OptionCategory MyToolCategory("my-tool options");

// CommonOptionsParser declares HelpMessage with a description of the common
// command-line options related to the compilation database and input files.
// It's nice to have this help message in all tools.
static cl::extrahelp CommonHelp(CommonOptionsParser::HelpMessage);

// A help message for this specific tool can be added afterwards.
static cl::extrahelp MoreHelp("\nMore help text...");

int main(int argc, const char **argv) {
  CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());

  MyPrinter Printer;
  MatchFinder Finder;
  
  const auto AllPointerTypes = anyOf(
      hasType(pointerType()), hasType(autoType(hasDeducedType(pointerType()))),
      hasType(decltypeType(hasUnderlyingType(pointerType()))));

  StatementMatcher indexingMatcher = arraySubscriptExpr().bind("operation");
		  
  Finder.addMatcher(indexingMatcher, &Printer);
  
  return Tool.run(newFrontendActionFactory(&Finder).get());
}