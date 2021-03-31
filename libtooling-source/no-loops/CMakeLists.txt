set(LLVM_LINK_COMPONENTS Support)

add_clang_executable(no-loops
  NoLoops.cpp
  )

target_link_libraries(no-loops
  PRIVATE
  clangTooling
  clangBasic
  clangASTMatchers
  )

install(TARGETS no-loops
        RUNTIME DESTINATION bin
        COMPONENT clang-extras)
