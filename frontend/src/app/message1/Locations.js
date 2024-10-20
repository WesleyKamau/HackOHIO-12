"use client";
import React, { useState } from 'react';
import { 
    Select,
    SelectTrigger,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectValue
 } from '@/components/ui/select';

const campusLocations = {
    North: [
        {value: "1", label: 'Archer House'},
        {value: "2", label: 'Barrett House'},
        {value: "3", label: 'Blackburn House'},
        {value: "4", label: 'Bowen House'},
        {value: "5", label: 'Busch House'},
        {value: "6", label: 'Drackett Tower'},
        {value: "7", label: 'Halloran House'},
        {value: "8", label: 'Haverfield House'},
        {value: "9", label: 'Houck House'},
        {value: "10", label: 'Houston House'},
        {value: "11", label: 'Jones Tower'},
        {value: "12", label: 'Lawrence Tower'},
        {value: "13", label: 'Mendoza House'},
        {value: "14", label: 'Norton House'},
        {value: "15", label: 'Nosker House'},
        {value: "16", label: 'Raney House'},
        {value: "17", label: 'Scott House'},
        {value: "18", label: 'Taylor Tower'},
        {value: "19", label: 'Torres House'},
    ],
    South: [
        {value: "20", label: 'Baker Hall East'},
        {value: "21", label: 'Baker Hall West'},
        {value: "22", label: 'Bradley Hall'},
        {value: "23", label: 'Canfield Hall'},
        {value: "24", label: 'Fechko House'},
        {value: "25", label: 'German House'},
        {value: "26", label: 'Hanley House'},
        {value: "27", label: 'Mack Hall'},
        {value: "28", label: 'Morrison Tower'},
        {value: "29", label: 'Neil Building'},
        {value: "30", label: 'Park-Stradley Hall'},
        {value: "31", label: 'Paterson Hall'},
        {value: "32", label: 'Pennsylvania Place'},
        {value: "33", label: 'Pomerene House'},
        {value: "34", label: 'Scholars East'},
        {value: "35", label: 'Scholars West'},
        {value: "36", label: 'Siebert Hall'},
        {value: "37", label: 'Smith-Steeb Hall'},
        {value: "38", label: 'The Residence on Tenth'},
        {value: "39", label: 'Worthington Building'},
    ],
    West: [
        {value: "40", label: 'Lincoln Tower'},
        {value: "41", label: 'Morrill Tower'},
    ]
}

export default function Locations() {
    const [selectedCampuses, setSelectedCampuses] = useState([]);
    const [selectedDorms, setSelectedDorms] = useState([]);

    const handleCampusChange = (e) => {
        setSelectedCampuses((prev) =>
            prev.includes(e)
            ? prev.filter((campus) => campus !== e)
            : [...prev, e]
        );
        setSelectedDorms([]); // Reset dorm selection when campus changes
    };

    const handleDormChange = (e) => {
        setSelectedDorms((prev) =>
            prev.includes(e)
            ? prev.filter((dorm) => dorm !== e)
            : [...prev, e]
        );
    };

    return (
        <div>
            <h2>Select Campuses</h2>
            <Select onValueChange={handleCampusChange} multiple>
                <SelectTrigger className="w-[280px]">
                 <SelectValue placeholder="Select regions on campus."/>
                </SelectTrigger>
                <SelectContent>
                    <SelectGroup>
                        <SelectItem value="North">North</SelectItem>
                        <SelectItem value="South">South</SelectItem>
                        <SelectItem value="West">West</SelectItem>
                    </SelectGroup>
                </SelectContent>
            </Select>

            {selectedCampuses.length > 0 && (
                <>
                    <h2>Select Dorms</h2>
                    <Select onValueChange={handleDormChange} multiple>
                        <SelectTrigger className="w-[280px]">
                            <SelectValue placeholder="Select dorms."/>
                        </SelectTrigger>
                        <SelectContent>
                            {selectedCampuses.map(campus => (
                                <SelectGroup key={campus} label={campus}>
                                    {campusLocations[campus].map(dorm => (
                                        <SelectItem key={dorm.value} value={dorm.value}>
                                            {dorm.label}
                                        </SelectItem>
                                    ))}
                                </SelectGroup>
                            ))}
                        </SelectContent>
                    </Select>
                </>
            )}
        </div>
    );
}
