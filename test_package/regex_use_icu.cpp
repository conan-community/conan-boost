#include <boost/regex/icu.hpp>
#include <iostream>

int main(int argc, const char * const argv[])
{
    return boost::u32regex_match( "Is icu 図書館 there ?", boost::make_u32regex( "書" ) );       
}