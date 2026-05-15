import TrendsExplorer from "./TrendsExplorer";
import { loadThemeData } from "./themeData";

export default function Home() {
  const themeData = loadThemeData();
  return <TrendsExplorer themeData={themeData} />;
}
