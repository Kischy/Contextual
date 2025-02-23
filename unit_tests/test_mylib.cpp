#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "mylib.hpp"

using namespace testing;

TEST(MyLibTest, AddTest) {
    MyLib lib;
    EXPECT_THAT(lib.add(2, 3), Eq(5));

}
