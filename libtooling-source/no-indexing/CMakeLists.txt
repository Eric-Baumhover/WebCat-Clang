set(LLVM_LINK_COMPONENTS support)

add_clang_executable(no-indexing
  NoIndexing.cpp
  )
target_link_libraries(no-indexing
  PRIVATE
  clangTooling
  clangBasic
  clangASTMatchers
  )

install(TARGETS no-indexing
        RUNTIME DESTINATION bin
        COMPONENT clang-extras)
