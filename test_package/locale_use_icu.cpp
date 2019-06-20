#include <boost/locale.hpp>
#include <boost/range/algorithm/find.hpp>

int main(int argc, const char * const argv[])
{
  auto backends = boost::locale::localization_backend_manager::global().get_all_backends();

  return ! ( boost::find( backends, "icu" ) != backends.end() );
}
