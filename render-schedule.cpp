#include <fstream>
#include <nlohmann/json.hpp>
using nlohmann::json;

std::ifstream f("schedule.json");
json data = json::parse(schedule);

