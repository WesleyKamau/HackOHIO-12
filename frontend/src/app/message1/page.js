import Locations from "./Locations";
import UploadFlyer from "./uploadFlyer";
import EventInput from "./EventInput";
import './Styling.css';

export default function Home() {
  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <h1 className="title">Disseminate Your Event with GroupMe Bot!</h1> 
      <p className="description">Upload a flyer and share the info to dorms of your specification.</p>
      <UploadFlyer/>
      <Locations/>
      <EventInput/>
    </div>
  );
}
