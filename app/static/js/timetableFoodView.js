/**
 * Servo AI - Timetable-Based Food & Kitchen Planning Studio ("Steam & Ledger")
 * 100% Client-Side Ingestion, Schedule Analysis, Meal Portioning & Kitchen Prep Planner.
 */

const round = (val, dec = 1) => Number(Math.round(Number(val + 'e' + dec)) + 'e-' + dec);

// Realistic Default Timetable Dataset for Instant 1-Click Demo & Template Generation
export function generateSampleTimetableCSV() {
  return `day,time_slot,start_time,end_time,department,year_section,student_count,activity_type,location,notes
Monday,08:30-09:30,08:30,09:30,Computer Science,CS-A 3rd Year,75,Lecture,CS Block 101,Theory - Operating Systems
Monday,08:30-09:30,08:30,09:30,Mechanical Eng,ME-B 2nd Year,65,Lecture,Mech Block 204,Applied Thermodynamics
Monday,08:30-10:30,08:30,10:30,Electronics,EC-A 1st Year,70,Lab,VLSI Lab,Early Lab Session - Commuter rush
Monday,09:30-10:30,09:30,10:30,Information Tech,IT-A 4th Year,80,Lecture,IT Block 302,Distributed Cloud Systems
Monday,09:30-10:30,09:30,10:30,Civil Eng,CE-A 3rd Year,60,Lecture,Civil Block 105,Structural Concrete Design
Monday,10:30-11:00,10:30,11:00,Campus Wide,All Departments,850,Break,Canteen & Quad,Morning Tea Break - Heavy Chai & Samosa Rush
Monday,11:00-13:00,11:00,13:00,Computer Science,CS-B 2nd Year,75,Lab,AI Lab 2,Data Structures & Algorithms Lab
Monday,11:00-12:00,11:00,12:00,MBA,MBA 1st Year,120,Lecture,Management Block,Financial Accounting
Monday,12:00-13:00,12:00,13:00,Mechanical Eng,ME All Batches,260,Lunch Break,Canteen Block,Batch 1 Lunch - Early Release Line
Monday,12:00-13:00,12:00,13:00,Civil Eng,CE All Batches,190,Lunch Break,Canteen Block,Batch 1 Lunch - Early Release Line
Monday,13:00-14:00,13:00,14:00,Computer Science,CS All Batches,340,Lunch Break,Canteen Block,Batch 2 Lunch - Main Peak Surge
Monday,13:00-14:00,13:00,14:00,Electronics,EC All Batches,290,Lunch Break,Canteen Block,Batch 2 Lunch - Main Peak Surge
Monday,13:00-14:00,13:00,14:00,Biotechnology,BT All Batches,160,Lunch Break,Canteen Block,Batch 2 Lunch - Main Peak Surge
Monday,14:00-16:00,14:00,16:00,Mechanical Eng,ME-A 3rd Year,70,Lab,Workshop Lab,Welding & Foundry Workshop
Monday,15:00-16:00,15:00,16:00,Computer Science,CS-A 4th Year,85,Lecture,Seminar Hall,Compiler Design
Monday,16:00-17:00,16:00,17:00,Campus Wide,All Departments,980,Break,Canteen & Lawns,Evening Dismissal - Massive Snack & Tea Rush
Monday,17:00-19:00,17:00,19:00,Sports & Clubs,Hostel Students,320,Sports/Free,Sports Complex,Evening Fitness & Fresh Juice
Monday,19:30-21:30,19:30,21:30,Hostels,Hostel Residents & Staff,540,Dinner,Canteen Dining Hall,Night Dinner Service (Phulkas & Dal)
Tuesday,08:30-10:30,08:30,10:30,Mechanical Eng,ME-A 4th Year,70,Lab,CAD Lab,Simulation & Modeling
Tuesday,08:30-09:30,08:30,09:30,Computer Science,CS-B 3rd Year,75,Lecture,CS Block 102,Database Engineering
Tuesday,09:30-10:30,09:30,10:30,Biotechnology,BT-A 2nd Year,60,Lecture,Bio Block 201,Cell Biology
Tuesday,10:30-11:00,10:30,11:00,Campus Wide,All Departments,820,Break,Canteen & Quad,Morning Tea Break - High Beverage Surge
Tuesday,11:00-13:00,11:00,13:00,Electronics,EC-B 3rd Year,70,Lab,DSP Lab,Signal Processing Lab
Tuesday,12:00-13:00,12:00,13:00,Computer Science,CS All Batches,330,Lunch Break,Canteen Block,Batch 1 Lunch - Fast Food Line
Tuesday,12:00-13:00,12:00,13:00,MBA,MBA All Batches,140,Lunch Break,Canteen Block,Batch 1 Lunch - Executive Thali
Tuesday,13:00-14:00,13:00,14:00,Mechanical Eng,ME All Batches,270,Lunch Break,Canteen Block,Batch 2 Lunch - Main Biryani Rush
Tuesday,13:00-14:00,13:00,14:00,Civil Eng,CE All Batches,190,Lunch Break,Canteen Block,Batch 2 Lunch - Main Biryani Rush
Tuesday,13:00-14:00,13:00,14:00,Electronics,EC All Batches,280,Lunch Break,Canteen Block,Batch 2 Lunch - Main Biryani Rush
Tuesday,14:00-16:00,14:00,16:00,Civil Eng,CE-B 2nd Year,65,Lab,Survey Lab,Field Survey Practical
Tuesday,16:00-17:00,16:00,17:00,Campus Wide,All Departments,920,Break,Canteen & Lawns,Evening Class Dismissal - Samosa & Vada Pav Rush
Tuesday,19:30-21:30,19:30,21:30,Hostels,Residents & Faculty,530,Dinner,Canteen Dining Hall,Night Dinner (Jeera Rice & Paneer Curry)
Wednesday,08:30-10:30,08:30,10:30,Computer Science,CS-A 2nd Year,75,Lab,Python Lab,Object Oriented Programming
Wednesday,09:30-10:30,09:30,10:30,Electronics,EC-A 3rd Year,70,Lecture,EC Block 202,Microcontrollers
Wednesday,10:30-11:00,10:30,11:00,Campus Wide,All Departments,840,Break,Canteen & Quad,Morning Tea Break - Chai & Biscuits
Wednesday,11:00-13:00,11:00,13:00,Mechanical Eng,ME-B 3rd Year,65,Lab,Thermal Lab,Heat Transfer Practical
Wednesday,12:00-13:00,12:00,13:00,Electronics,EC All Batches,290,Lunch Break,Canteen Block,Batch 1 Lunch - South Indian Thali
Wednesday,12:00-13:00,12:00,13:00,Biotechnology,BT All Batches,160,Lunch Break,Canteen Block,Batch 1 Lunch - South Indian Thali
Wednesday,13:00-14:00,13:00,14:00,Computer Science,CS All Batches,340,Lunch Break,Canteen Block,Batch 2 Lunch - Peak Meal Rush
Wednesday,13:00-14:00,13:00,14:00,Mechanical Eng,ME All Batches,260,Lunch Break,Canteen Block,Batch 2 Lunch - Peak Meal Rush
Wednesday,13:00-14:00,13:00,14:00,Civil Eng,CE All Batches,180,Lunch Break,Canteen Block,Batch 2 Lunch - Peak Meal Rush
Wednesday,16:00-17:00,16:00,17:00,Campus Wide,All Departments,960,Break,Canteen & Lawns,Evening Class Dismissal - Cutlets & Chai
Wednesday,19:30-21:30,19:30,21:30,Hostels,Residents & Faculty,535,Dinner,Canteen Dining Hall,Night Dinner (Egg/Veg Curry & Rotis)
Thursday,08:30-09:30,08:30,09:30,Information Tech,IT-B 3rd Year,75,Lecture,IT Block 102,Computer Networks
Thursday,09:30-10:30,09:30,10:30,Civil Eng,CE-A 4th Year,60,Lecture,Civil Block 204,Geotechnical Engineering
Thursday,10:30-11:00,10:30,11:00,Campus Wide,All Departments,830,Break,Canteen & Quad,Morning Tea Break
Thursday,11:00-13:00,11:00,13:00,Biotechnology,BT-A 3rd Year,60,Lab,Microbiology Lab,Sterilization & Cultures
Thursday,12:00-13:00,12:00,13:00,Civil Eng,CE All Batches,190,Lunch Break,Canteen Block,Batch 1 Lunch
Thursday,12:00-13:00,12:00,13:00,Mechanical Eng,ME All Batches,260,Lunch Break,Canteen Block,Batch 1 Lunch
Thursday,13:00-14:00,13:00,14:00,Computer Science,CS All Batches,340,Lunch Break,Canteen Block,Batch 2 Lunch - High Volume
Thursday,13:00-14:00,13:00,14:00,Electronics,EC All Batches,290,Lunch Break,Canteen Block,Batch 2 Lunch - High Volume
Thursday,16:00-17:00,16:00,17:00,Campus Wide,All Departments,940,Break,Canteen & Lawns,Evening Dismissal
Thursday,19:30-21:30,19:30,21:30,Hostels,Residents & Faculty,525,Dinner,Canteen Dining Hall,Night Dinner Service
Friday,08:30-10:30,08:30,10:30,Computer Science,CS-A 1st Year,80,Lab,Basic Electronics Lab,Circuit Labs
Friday,10:30-11:00,10:30,11:00,Campus Wide,All Departments,860,Break,Canteen & Quad,Morning Tea Break
Friday,12:00-13:00,12:00,13:00,Computer Science,CS All Batches,330,Lunch Break,Canteen Block,Batch 1 Lunch - Friday Special Biryani
Friday,12:00-13:00,12:00,13:00,MBA,MBA All Batches,130,Lunch Break,Canteen Block,Batch 1 Lunch - Friday Special Biryani
Friday,13:00-14:00,13:00,14:00,Mechanical Eng,ME All Batches,250,Lunch Break,Canteen Block,Batch 2 Lunch - Friday Special Biryani
Friday,13:00-14:00,13:00,14:00,Electronics,EC All Batches,270,Lunch Break,Canteen Block,Batch 2 Lunch - Friday Special Biryani
Friday,13:00-14:00,13:00,14:00,Civil Eng,CE All Batches,170,Lunch Break,Canteen Block,Batch 2 Lunch - Friday Special Biryani
Friday,15:30-17:00,15:30,17:00,Campus Wide,All Departments,990,Break,Canteen & Main Gate,Friday Weekend Taper & Evening Snacks
Friday,19:30-21:30,19:30,21:30,Hostels,Hostel Students,460,Dinner,Canteen Dining Hall,Friday Night Hostel Dinner
Saturday,09:00-13:00,09:00,13:00,Project Labs,Final Year Teams,180,Workshop,Innovation Lab,Weekend Capstone Projects
Saturday,10:30-11:00,10:30,11:00,Campus Wide,Weekend Attendees,240,Break,Canteen,Weekend Morning Refreshment
Saturday,12:30-14:00,12:30,14:00,Campus Wide,Weekend Residents & Scholars,310,Lunch Break,Canteen,Saturday Buffet Lunch
Saturday,16:00-17:30,16:00,17:30,Hostels,Resident Students,220,Break,Canteen,Weekend Evening Chai
Saturday,19:30-21:30,19:30,21:30,Hostels,Resident Students,380,Dinner,Canteen Dining Hall,Saturday Night Dinner
Sunday,08:30-11:00,08:30,11:00,Hostels,Residents,280,Break,Canteen Dining Hall,Sunday Special Brunch (Dosa & Puri)
Sunday,13:00-14:30,13:00,14:30,Hostels,Residents,310,Lunch Break,Canteen Dining Hall,Sunday Feast
Sunday,16:30-18:00,16:30,18:00,Hostels,Residents,200,Break,Canteen,Sunday Evening Chai
Sunday,19:30-21:30,19:30,21:30,Hostels,Residents,350,Dinner,Canteen Dining Hall,Sunday Night Dinner`;
}

export class TimetableFoodView {
  constructor(containerEl, onOpenAssistant) {
    this.container = containerEl;
    this.onOpenAssistant = onOpenAssistant;
    this.timetableData = [];
    this.analyzedPlan = null;
    this.selectedDay = 'All';
    this.diningFactor = 0.80; // 80% dining attendance factor
    this.safetyBufferPct = 5.0; // 5% safety buffer for grocery
    this.searchQuery = '';
  }

  async load() {
    if (!this.timetableData.length) {
      // Auto-load demo timetable data so user sees immediate value
      this.timetableData = this.parseCSV(generateSampleTimetableCSV());
      this.computeFoodPlan();
    }
    this.render();
  }

  // Pure JavaScript Client-Side CSV Parser
  parseCSV(text) {
    if (!text || !text.trim()) return [];
    const lines = text.trim().split(/\r?\n/);
    if (lines.length < 2) return [];

    const header = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/['"]/g, ''));
    
    // Column index lookup with flexible alias mappings
    const getColIdx = (aliases) => {
      for (const a of aliases) {
        const idx = header.indexOf(a);
        if (idx !== -1) return idx;
      }
      return -1;
    };

    const dayIdx = getColIdx(['day', 'weekday', 'day_of_week']);
    const slotIdx = getColIdx(['time_slot', 'slot', 'time', 'timing', 'period']);
    const startIdx = getColIdx(['start_time', 'start', 'from']);
    const endIdx = getColIdx(['end_time', 'end', 'to']);
    const deptIdx = getColIdx(['department', 'dept', 'branch', 'stream']);
    const batchIdx = getColIdx(['year_section', 'year', 'section', 'batch', 'class']);
    const countIdx = getColIdx(['student_count', 'students', 'count', 'strength', 'headcount', 'capacity', 'qty']);
    const actIdx = getColIdx(['activity_type', 'activity', 'type', 'subject', 'event', 'session']);
    const locIdx = getColIdx(['location', 'room', 'hall', 'building', 'venue']);
    const notesIdx = getColIdx(['notes', 'remarks', 'comment', 'description']);

    const records = [];

    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      // Handle quoted CSV fields
      const row = [];
      let inQuote = false;
      let curVal = '';
      for (let c = 0; c < line.length; c++) {
        const char = line[c];
        if (char === '"') {
          inQuote = !inQuote;
        } else if (char === ',' && !inQuote) {
          row.push(curVal.trim());
          curVal = '';
        } else {
          curVal += char;
        }
      }
      row.push(curVal.trim());

      const rawCount = countIdx !== -1 ? parseInt(row[countIdx]) : 60;
      const count = isNaN(rawCount) || rawCount <= 0 ? 60 : rawCount;

      const day = dayIdx !== -1 ? row[dayIdx] : 'Monday';
      const slot = slotIdx !== -1 ? row[slotIdx] : '12:00-13:00';
      const start = startIdx !== -1 && row[startIdx] ? row[startIdx] : slot.split('-')[0] || '12:00';
      const end = endIdx !== -1 && row[endIdx] ? row[endIdx] : slot.split('-')[1] || '13:00';
      const dept = deptIdx !== -1 ? row[deptIdx] : 'General';
      const batch = batchIdx !== -1 ? row[batchIdx] : 'Batch A';
      const act = actIdx !== -1 ? row[actIdx] : 'Lecture';
      const loc = locIdx !== -1 ? row[locIdx] : 'Campus Block';
      const notes = notesIdx !== -1 ? row[notesIdx] : '';

      records.push({
        id: i,
        day: day.charAt(0).toUpperCase() + day.slice(1).toLowerCase(),
        time_slot: slot,
        start_time: start.trim(),
        end_time: end.trim(),
        department: dept,
        year_section: batch,
        student_count: count,
        activity_type: act,
        location: loc,
        notes: notes
      });
    }

    return records;
  }

  // 100% Client-Side Timetable Food Requirement & Rush Hour Modeling Engine
  computeFoodPlan() {
    if (!this.timetableData.length) {
      this.analyzedPlan = null;
      return;
    }

    // Filter by selected day or calculate aggregate
    const records = this.selectedDay === 'All'
      ? this.timetableData
      : this.timetableData.filter(r => r.day.toLowerCase() === this.selectedDay.toLowerCase());

    const totalDaysCount = this.selectedDay === 'All'
      ? new Set(this.timetableData.map(r => r.day)).size || 7
      : 1;

    let totalScheduledStudents = 0;
    let morningHeadcount = 0;
    let midMorningBreakHeadcount = 0;
    let batch1LunchHeadcount = 0;
    let batch2LunchHeadcount = 0;
    let eveningBreakHeadcount = 0;
    let nightDinnerHeadcount = 0;

    const hourlyLoad = {
      "08:00": 0, "09:00": 0, "10:00": 0, "11:00": 0,
      "12:00": 0, "13:00": 0, "14:00": 0, "15:00": 0,
      "16:00": 0, "17:00": 0, "18:00": 0, "19:00": 0, "20:00": 0
    };

    records.forEach(r => {
      const count = r.student_count;
      totalScheduledStudents += count;

      const actLower = r.activity_type.toLowerCase();
      const startHour = parseInt(r.start_time.split(':')[0]) || 9;

      // Map hourly load
      const hourKey = `${startHour.toString().padStart(2, '0')}:00`;
      if (hourlyLoad[hourKey] !== undefined) {
        hourlyLoad[hourKey] += count;
      }

      // Slot classifications
      if (startHour >= 7 && startHour <= 9) {
        morningHeadcount += count;
      } else if (startHour === 10 || (actLower.includes('break') && startHour < 12)) {
        midMorningBreakHeadcount += count;
      } else if (startHour === 12 || (actLower.includes('lunch') && startHour < 13)) {
        batch1LunchHeadcount += count;
      } else if (startHour === 13 || (actLower.includes('lunch') && startHour < 14)) {
        batch2LunchHeadcount += count;
      } else if (startHour >= 15 && startHour <= 17) {
        eveningBreakHeadcount += count;
      } else if (startHour >= 18 || actLower.includes('dinner')) {
        nightDinnerHeadcount += count;
      }
    });

    // Normalize daily metrics if viewing weekly aggregate
    const divisor = this.selectedDay === 'All' ? Math.max(1, totalDaysCount) : 1;
    
    // Applied dining factor & realistic canteen conversion
    const b_covers = Math.round((morningHeadcount / divisor) * 0.45 + 180 * this.diningFactor);
    const l_covers = Math.round(((batch1LunchHeadcount + batch2LunchHeadcount) / divisor) * this.diningFactor);
    const s_covers = Math.round(((midMorningBreakHeadcount + eveningBreakHeadcount) / divisor) * 0.65);
    const d_covers = Math.round((nightDinnerHeadcount / divisor) * 0.85 + 240 * this.diningFactor);
    const total_meals = b_covers + l_covers + s_covers + d_covers;

    // Buffer multiplier
    const bufferMult = 1.0 + (this.safetyBufferPct / 100.0);
    const mainMeals = l_covers + d_covers;

    // Standardized Pantry Grocery Requisitions based on timetable food demand
    const riceKg = round((mainMeals * 0.14) * bufferMult, 1);       // 140g per main meal
    const dalKg = round((mainMeals * 0.055) * bufferMult, 1);       // 55g per main meal
    const vegKg = round((mainMeals * 0.12 + s_covers * 0.04) * bufferMult, 1); // 120g lunch/dinner + 40g snack
    const milkL = round((b_covers * 0.08 + s_covers * 0.12 + mainMeals * 0.04) * bufferMult, 1); // Chai, curd, coffee
    const oilL = round((mainMeals * 0.032 + s_covers * 0.02) * bufferMult, 1); // Cooking medium & frying
    const attaKg = round((mainMeals * 0.075) * bufferMult, 1);      // Phulkas & Rotis

    const estCost = Math.round(
      riceKg * 58.0 + dalKg * 145.0 + vegKg * 42.0 + milkL * 64.0 + oilL * 135.0 + attaKg * 40.0 + (s_covers * 12.0)
    );

    // Identify Peak Rush Times
    let peakHour = "13:00";
    let maxHourCount = 0;
    Object.entries(hourlyLoad).forEach(([h, count]) => {
      if (count > maxHourCount) {
        maxHourCount = count;
        peakHour = h;
      }
    });

    const b1Daily = Math.round(batch1LunchHeadcount / divisor);
    const b2Daily = Math.round(batch2LunchHeadcount / divisor);

    // Kitchen Bell Schedule (Batch Cooking Timeline)
    const prepTimeline = [
      {
        time: "06:45 AM",
        shift: "Breakfast Prep",
        task: `Start boiling Sambar & steaming ${Math.round(b_covers * 0.55)} Idlis. Warm Tawa for Dosa station.`,
        rushBell: "07:45 AM – 09:15 AM (Commuters & Hostelers)",
        targetCovers: b_covers
      },
      {
        time: "09:45 AM",
        shift: "Morning Tea Rush",
        task: `Brew 25L Cardamom Chai & prep ${Math.round(s_covers * 0.35)} warm Samosas/Poha for mid-morning class interval.`,
        rushBell: "10:30 AM – 11:00 AM (Class Interval Bell)",
        targetCovers: Math.round(s_covers * 0.35)
      },
      {
        time: "11:15 AM",
        shift: "Batch 1 Lunch Prep",
        task: `Steam first ${Math.round(riceKg * 0.45)} kg Basmati Rice batch & simmer Tadka Dal for Early Lunch release (Mech & Civil).`,
        rushBell: `12:00 PM – 12:55 PM (~${b1Daily} students)`,
        targetCovers: Math.round(l_covers * (b1Daily / Math.max(1, b1Daily + b2Daily)))
      },
      {
        time: "12:30 PM",
        shift: "Batch 2 Peak Lunch",
        task: `Uncover fresh dum Biryani & roll hot Phulkas for Peak Crowd (CS, EC, Biotech releases).`,
        rushBell: `01:00 PM – 02:00 PM (~${b2Daily} students - High Surge!)`,
        targetCovers: Math.round(l_covers * (b2Daily / Math.max(1, b1Daily + b2Daily)))
      },
      {
        time: "03:15 PM",
        shift: "Evening Snacks & Tea",
        task: `Deep-fry fresh Samosas & Vada Pavs. Brew double-batch Masala Chai & Filter Coffee.`,
        rushBell: "04:00 PM – 05:00 PM (Class Dismissal Bell)",
        targetCovers: Math.round(s_covers * 0.65)
      },
      {
        time: "06:30 PM",
        shift: "Night Dinner Service",
        task: `Cook Dinner Gravies (Paneer/Chicken Curry, Jeera Rice & fresh Phulkas).`,
        rushBell: "07:30 PM – 09:30 PM (Hostel Dining)",
        targetCovers: d_covers
      }
    ];

    this.analyzedPlan = {
      totalRecords: records.length,
      totalScheduledStudents: totalScheduledStudents,
      dailyAverageScheduled: Math.round(totalScheduledStudents / divisor),
      covers: {
        breakfast: b_covers,
        lunch: l_covers,
        snacks: s_covers,
        dinner: d_covers,
        total: total_meals
      },
      staggeredLunch: {
        batch1_headcount: b1Daily,
        batch2_headcount: b2Daily,
        batch1_covers: Math.round(l_covers * 0.42),
        batch2_covers: Math.round(l_covers * 0.58)
      },
      pantry: {
        rice_kg: riceKg,
        dal_kg: dalKg,
        veg_kg: vegKg,
        milk_l: milkL,
        oil_l: oilL,
        atta_kg: attaKg,
        est_cost: estCost
      },
      peakRush: {
        hour: peakHour,
        count: Math.round(maxHourCount / divisor),
        description: peakHour.startsWith("12") || peakHour.startsWith("13")
          ? "Peak Staggered Lunch Rush (CS, Mech, EC Releases)"
          : peakHour.startsWith("16")
          ? "Evening Campus Dismissal Snack Surge"
          : "Morning Lecture & Lab Arrival Flow"
      },
      hourlyLoad: hourlyLoad,
      prepTimeline: prepTimeline
    };
  }

  render() {
    const daysList = ['All', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const p = this.analyzedPlan;

    // Filter table records by day and search
    let tableRecords = this.timetableData;
    if (this.selectedDay !== 'All') {
      tableRecords = tableRecords.filter(r => r.day.toLowerCase() === this.selectedDay.toLowerCase());
    }
    if (this.searchQuery) {
      const q = this.searchQuery.toLowerCase();
      tableRecords = tableRecords.filter(r => 
        r.department.toLowerCase().includes(q) ||
        r.year_section.toLowerCase().includes(q) ||
        r.activity_type.toLowerCase().includes(q) ||
        r.location.toLowerCase().includes(q) ||
        r.time_slot.toLowerCase().includes(q)
      );
    }

    this.container.innerHTML = `
      <!-- TOP SECTION HEADER -->
      <div class="section-header-block">
        <div>
          <h2 class="section-title">
            <i data-lucide="clock" style="color:var(--accent-copper); width:20px; height:20px;"></i>
            Timetable-Based Food & Kitchen Planning Studio
          </h2>
          <span style="font-size:12px; color:var(--text-secondary);">
            Ingests class schedules & timetable CSVs to automatically calculate meal demand, stagger lunch batches, time kitchen prep, and requisition pantry ingredients.
          </span>
        </div>

        <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
          <button class="btn-secondary" id="btn-dl-timetable-template" style="padding: 6px 14px; font-size:12px;">
            <i data-lucide="download" style="width:13px; height:13px;"></i> Download Timetable Template (CSV)
          </button>
          <button class="btn-primary" id="btn-export-food-plan" style="padding: 6px 14px; font-size:12px;">
            <i data-lucide="file-check" style="width:13px; height:13px;"></i> Export Food Plan (CSV)
          </button>
        </div>
      </div>

      <!-- TIMETABLE INGESTION & CONTROLS CARD -->
      <div class="hero-prediction-card" style="margin-bottom: 24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 16px; flex-wrap:wrap; gap:12px;">
          <div>
            <h3 style="font-family:var(--font-display); font-size:16px; font-weight:700; color:var(--text-primary); margin-bottom:2px;">
              1. Ingest Timetable Schedule CSV
            </h3>
            <div style="font-size:12px; color:var(--text-secondary);">
              Columns: <code style="font-family:var(--font-mono); color:var(--accent-copper); background:var(--bg-chalkboard); padding:2px 6px; border-radius:4px;">day, time_slot, department, student_count, activity_type, location</code>
            </div>
          </div>

          <!-- SLIDER CONTROLS -->
          <div style="display:flex; gap:12px; flex-wrap:wrap;">
            <!-- Attendance / Dining Factor -->
            <div style="display:flex; align-items:center; gap:8px; background:var(--bg-chalkboard); padding:6px 12px; border-radius:var(--radius-md); border:1px solid var(--border-subtle);">
              <label style="font-size:11px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin:0;">
                Dining Attendance:
              </label>
              <input type="range" id="tt-dining-slider" min="40" max="100" step="5" value="${Math.round(this.diningFactor * 100)}" style="width:75px; cursor:pointer;" />
              <span id="tt-dining-val" style="font-family:var(--font-mono); font-weight:700; color:var(--accent-copper); font-size:12px; min-width:32px;">
                ${Math.round(this.diningFactor * 100)}%
              </span>
            </div>

            <!-- Safety Buffer -->
            <div style="display:flex; align-items:center; gap:8px; background:var(--bg-chalkboard); padding:6px 12px; border-radius:var(--radius-md); border:1px solid var(--border-subtle);">
              <label style="font-size:11px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin:0;">
                Pantry Buffer:
              </label>
              <input type="range" id="tt-buffer-slider" min="0" max="25" step="1" value="${this.safetyBufferPct}" style="width:75px; cursor:pointer;" />
              <span id="tt-buffer-val" style="font-family:var(--font-mono); font-weight:700; color:var(--color-sage); font-size:12px; min-width:32px;">
                +${this.safetyBufferPct}%
              </span>
            </div>
          </div>
        </div>

        <!-- DROPZONE -->
        <div class="csv-dropzone" id="tt-csv-dropzone" style="padding: 24px 20px;">
          <input type="file" id="tt-file-input" accept=".csv,text/csv,.pdf" style="display:none;" />
          <div class="dropzone-inner">
            <div class="dropzone-icon-wrap" style="width:52px; height:52px; margin-bottom:10px;">
              <i data-lucide="calendar-clock" style="width:28px; height:28px; color:var(--accent-copper);"></i>
            </div>
            <div style="font-family:var(--font-display); font-size:15px; font-weight:600; color:var(--text-primary); margin-bottom:4px;">
              Drop your College Timetable (CSV/PDF) here
            </div>
            <div style="font-size:12px; color:var(--text-secondary); margin-bottom:12px;">
              CSV parsing is client-side. PDFs will be securely parsed.
            </div>

            <div style="display:flex; gap:10px; justify-content:center; flex-wrap:wrap;">
              <button class="btn-primary" id="btn-browse-tt-file" style="padding:6px 16px; font-size:12px;">
                <i data-lucide="folder-open" style="width:13px; height:13px;"></i> Select Timetable CSV/PDF
              </button>
              <button class="btn-secondary" id="btn-load-demo-tt" style="padding:6px 16px; font-size:12px;">
                <i data-lucide="sparkles" style="width:13px; height:13px; color:var(--accent-copper);"></i> Load Engineering Demo Schedule
              </button>
            </div>
          </div>
        </div>

        <!-- DAY SELECTION PILLS -->
        <div style="margin-top:16px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
          <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
            <span style="font-size:11.5px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin-right:4px;">
              Select Schedule Day:
            </span>
            ${daysList.map(d => `
              <button class="nav-tab-btn ${this.selectedDay === d ? 'active' : ''}" data-day="${d}" style="padding: 4px 10px; font-size:11.5px;">
                ${d}
              </button>
            `).join('')}
          </div>

          <div style="font-size:12px; color:var(--text-secondary); font-family:var(--font-mono);">
            Ingested: <b>${this.timetableData.length} scheduled class/lab slots</b>
          </div>
        </div>
      </div>

      <!-- ANALYZED FOOD PLAN & KITCHEN TIMETABLE -->
      ${p ? `
        <!-- 1. KPI SUMMARY TILES -->
        <div class="metrics-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:12px; margin-bottom:24px;">
          <div class="metric-box" style="background:var(--bg-surface); border:1px solid var(--border-subtle); padding:16px; border-radius:var(--radius-md);">
            <div style="font-size:11px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin-bottom:4px;">Daily Food Requirement</div>
            <div style="font-family:var(--font-display); font-size:26px; font-weight:700; color:var(--accent-copper);">${p.covers.total.toLocaleString()}</div>
            <div style="font-size:11px; color:var(--text-secondary); margin-top:2px;">Covers across 4 meal shifts</div>
          </div>

          <div class="metric-box" style="background:var(--bg-surface); border:1px solid var(--border-subtle); padding:16px; border-radius:var(--radius-md);">
            <div style="font-size:11px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin-bottom:4px;">Peak Canteen Bottleneck</div>
            <div style="font-family:var(--font-display); font-size:24px; font-weight:700; color:var(--text-cream-hero);">${p.peakRush.hour}</div>
            <div style="font-size:11px; color:var(--accent-copper); margin-top:2px;">${p.peakRush.count} students released</div>
          </div>

          <div class="metric-box" style="background:var(--bg-surface); border:1px solid var(--border-subtle); padding:16px; border-radius:var(--radius-md);">
            <div style="font-size:11px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin-bottom:4px;">Staggered Lunch Split</div>
            <div style="font-family:var(--font-mono); font-size:20px; font-weight:700; color:var(--text-primary); margin-top:4px;">
              B1: <b style="color:var(--accent-copper);">${p.staggeredLunch.batch1_covers}</b> | B2: <b style="color:var(--text-cream-hero);">${p.staggeredLunch.batch2_covers}</b>
            </div>
            <div style="font-size:11px; color:var(--text-secondary); margin-top:2px;">12:00 vs 13:00 releases</div>
          </div>

          <div class="metric-box" style="background:var(--bg-surface); border:1px solid var(--border-subtle); padding:16px; border-radius:var(--radius-md);">
            <div style="font-size:11px; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin-bottom:4px;">Pantry Grocery Requisition</div>
            <div style="font-family:var(--font-display); font-size:26px; font-weight:700; color:var(--color-sage);">₹${p.pantry.est_cost.toLocaleString()}</div>
            <div style="font-size:11px; color:var(--text-secondary); margin-top:2px;">Includes +${this.safetyBufferPct}% safety buffer</div>
          </div>
        </div>

        <!-- 2. STATION COVERS & FOOD DESIGN MATRIX -->
        <div class="hero-prediction-card" style="margin-bottom: 24px;">
          <div class="section-header-block" style="margin-bottom: 16px;">
            <div>
              <h3 class="section-title" style="font-size:15px;">
                <i data-lucide="utensils" style="color:var(--accent-copper); width:16px; height:16px;"></i>
                Timetable-Aligned Meal Portions & Food Design
              </h3>
              <span style="font-size:12px; color:var(--text-secondary);">
                Portions calculated according to student arrival timings, lecture releases, and lab schedules.
              </span>
            </div>
          </div>

          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:14px;">
            <!-- Breakfast -->
            <div style="background:var(--bg-chalkboard); border:1px solid var(--border-subtle); border-radius:var(--radius-md); padding:14px;">
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px;">
                <span style="font-weight:700; font-size:13px; color:var(--text-primary);">🍳 Breakfast Rush (07:30 - 09:30)</span>
                <span style="font-family:var(--font-mono); font-weight:700; color:var(--accent-copper); font-size:16px;">${p.covers.breakfast} covers</span>
              </div>
              <div style="font-size:12px; color:var(--text-secondary); line-height:1.5;">
                • <b>Quick Service:</b> Idli Sambar (350 pcs), Masala Dosa (140 pcs), Poha (45 kg)<br>
                • <b>Beverages:</b> Filter Coffee & Assam Tea (85L)
              </div>
            </div>

            <!-- Lunch -->
            <div style="background:var(--bg-chalkboard); border:1px solid rgba(201,113,61,0.4); border-radius:var(--radius-md); padding:14px;">
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px;">
                <span style="font-weight:700; font-size:13px; color:var(--accent-copper);">🍲 Staggered Lunch (12:00 - 14:30)</span>
                <span style="font-family:var(--font-mono); font-weight:700; color:var(--accent-copper); font-size:16px;">${p.covers.lunch} covers</span>
              </div>
              <div style="font-size:12px; color:var(--text-secondary); line-height:1.5;">
                • <b>Batch 1 (12:00):</b> ${p.staggeredLunch.batch1_covers} Thalis (Mech & Civil)<br>
                • <b>Batch 2 (13:00):</b> ${p.staggeredLunch.batch2_covers} Dum Biryani & Rotis (CS, EC, BT)<br>
                • <b>Pantry:</b> ${p.pantry.rice_kg} kg Rice • ${p.pantry.dal_kg} kg Dal
              </div>
            </div>

            <!-- Snacks -->
            <div style="background:var(--bg-chalkboard); border:1px solid var(--border-subtle); border-radius:var(--radius-md); padding:14px;">
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px;">
                <span style="font-weight:700; font-size:13px; color:var(--text-primary);">☕ Evening Snacks (16:00 - 18:00)</span>
                <span style="font-family:var(--font-mono); font-weight:700; color:var(--color-sage); font-size:16px;">${p.covers.snacks} covers</span>
              </div>
              <div style="font-size:12px; color:var(--text-secondary); line-height:1.5;">
                • <b>Dismissal Rush:</b> Hot Samosas (420 pcs), Vada Pav (260 pcs)<br>
                • <b>Fresh Beverages:</b> Masala Chai (65L), Cold Coffee (30L)
              </div>
            </div>

            <!-- Dinner -->
            <div style="background:var(--bg-chalkboard); border:1px solid var(--border-subtle); border-radius:var(--radius-md); padding:14px;">
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px;">
                <span style="font-weight:700; font-size:13px; color:var(--text-primary);">🌙 Hostel Dinner (19:30 - 21:30)</span>
                <span style="font-family:var(--font-mono); font-weight:700; color:var(--text-primary); font-size:16px;">${p.covers.dinner} covers</span>
              </div>
              <div style="font-size:12px; color:var(--text-secondary); line-height:1.5;">
                • <b>Mains:</b> Fresh Phulka Rotis (1,250 pcs), Paneer Butter Masala & Chicken Curry<br>
                • <b>Staples:</b> Jeera Rice & Tadka Dal
              </div>
            </div>
          </div>
        </div>

        <!-- 3. CHEF'S BELL SCHEDULE (BATCH COOKING TIMELINE) -->
        <div class="hero-prediction-card" style="margin-bottom: 24px;">
          <div class="section-header-block" style="margin-bottom: 14px;">
            <div>
              <h3 class="section-title" style="font-size:15px;">
                <i data-lucide="chef-hat" style="color:var(--accent-copper); width:16px; height:16px;"></i>
                Chef's Bell Schedule (Kitchen Batch Prep Timeline)
              </h3>
              <span style="font-size:12px; color:var(--text-secondary);">
                Timed 30-45 minutes ahead of college bell releases to ensure food is piping hot with minimal counter wait times.
              </span>
            </div>
          </div>

          <div style="display:flex; flex-direction:column; gap:10px;">
            ${p.prepTimeline.map(step => `
              <div style="display:flex; align-items:flex-start; gap:14px; background:var(--bg-chalkboard); border:1px solid var(--border-subtle); border-radius:var(--radius-md); padding:12px 16px;">
                <div style="background:var(--bg-surface); border:1px solid var(--accent-copper); border-radius:4px; padding:4px 8px; font-family:var(--font-mono); font-weight:700; color:var(--accent-copper); font-size:12px; white-space:nowrap;">
                  ${step.time}
                </div>
                <div style="flex:1;">
                  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px; flex-wrap:wrap;">
                    <span style="font-weight:700; font-size:13px; color:var(--text-primary);">${step.shift}</span>
                    <span class="unit-badge" style="font-size:11px;">🔔 Release Bell: ${step.rushBell}</span>
                  </div>
                  <div style="font-size:12px; color:var(--text-secondary); margin-top:2px;">
                    ${step.task}
                  </div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- 4. PANTRY GROCERY REQUISITION TABLE -->
        <div class="hero-prediction-card" style="margin-bottom: 24px;">
          <div class="section-header-block" style="margin-bottom: 14px;">
            <div>
              <h3 class="section-title" style="font-size:15px;">
                <i data-lucide="clipboard-list" style="color:var(--accent-copper); width:16px; height:16px;"></i>
                Timetable Raw Grocery Requisition
              </h3>
              <span style="font-size:12px; color:var(--text-secondary);">
                Raw ingredient requirements calculated for <b>${p.covers.total} covers</b> (+${this.safetyBufferPct}% buffer).
              </span>
            </div>
          </div>

          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap:10px;">
            <div style="background:var(--bg-chalkboard); padding:10px 14px; border-radius:6px; border:1px solid var(--border-subtle);">
              <span style="font-size:11px; color:var(--text-secondary);">🍚 Sona Masoori Rice</span>
              <div style="font-family:var(--font-mono); font-weight:700; font-size:16px; color:var(--text-primary);">${p.pantry.rice_kg} kg</div>
            </div>
            <div style="background:var(--bg-chalkboard); padding:10px 14px; border-radius:6px; border:1px solid var(--border-subtle);">
              <span style="font-size:11px; color:var(--text-secondary);">🥣 Toor & Moong Dal</span>
              <div style="font-family:var(--font-mono); font-weight:700; font-size:16px; color:var(--accent-copper);">${p.pantry.dal_kg} kg</div>
            </div>
            <div style="background:var(--bg-chalkboard); padding:10px 14px; border-radius:6px; border:1px solid var(--border-subtle);">
              <span style="font-size:11px; color:var(--text-secondary);">🥦 Mixed Seasonal Veg</span>
              <div style="font-family:var(--font-mono); font-weight:700; font-size:16px; color:var(--text-primary);">${p.pantry.veg_kg} kg</div>
            </div>
            <div style="background:var(--bg-chalkboard); padding:10px 14px; border-radius:6px; border:1px solid var(--border-subtle);">
              <span style="font-size:11px; color:var(--text-secondary);">🥛 Dairy Fresh Milk</span>
              <div style="font-family:var(--font-mono); font-weight:700; font-size:16px; color:var(--text-primary);">${p.pantry.milk_l} Litres</div>
            </div>
            <div style="background:var(--bg-chalkboard); padding:10px 14px; border-radius:6px; border:1px solid var(--border-subtle);">
              <span style="font-size:11px; color:var(--text-secondary);">🌻 Cooking Oil & Ghee</span>
              <div style="font-family:var(--font-mono); font-weight:700; font-size:16px; color:var(--text-primary);">${p.pantry.oil_l} Litres</div>
            </div>
            <div style="background:var(--bg-chalkboard); padding:10px 14px; border-radius:6px; border:1px solid var(--border-subtle);">
              <span style="font-size:11px; color:var(--text-secondary);">🌾 Whole Wheat Atta</span>
              <div style="font-family:var(--font-mono); font-weight:700; font-size:16px; color:var(--color-sage);">${p.pantry.atta_kg} kg</div>
            </div>
          </div>
        </div>

        <!-- 5. RAW TIMETABLE SCHEDULE TABLE -->
        <div class="data-table-container">
          <div style="padding:14px 18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; border-bottom:1px solid var(--border-subtle);">
            <div style="display:flex; align-items:center; gap:8px;">
              <i data-lucide="search" style="width:14px; height:14px; color:var(--text-secondary);"></i>
              <input type="text" id="tt-search-input" placeholder="Search department, slot, activity, room..." value="${this.searchQuery}" style="background:var(--bg-chalkboard); border:1px solid var(--border-subtle); color:var(--text-primary); padding:6px 12px; border-radius:var(--radius-sm); font-size:12px; width:260px;" />
            </div>

            <div style="font-size:12px; color:var(--text-secondary);">
              Showing <b>${tableRecords.length}</b> timetable entries (${this.selectedDay})
            </div>
          </div>

          <div style="overflow-x:auto;">
            <table class="canteen-table">
              <thead>
                <tr>
                  <th>Day & Slot</th>
                  <th>Department / Branch</th>
                  <th>Year / Batch</th>
                  <th>Scheduled Count</th>
                  <th>Activity Type</th>
                  <th>Location</th>
                  <th>Canteen Impact</th>
                </tr>
              </thead>
              <tbody>
                ${tableRecords.map(r => {
                  const isRush = r.activity_type.toLowerCase().includes('break') || r.activity_type.toLowerCase().includes('lunch');
                  return `
                    <tr>
                      <td>
                        <div style="font-family:var(--font-mono); font-weight:700; color:var(--text-primary); font-size:12.5px;">${r.time_slot}</div>
                        <div style="font-size:11px; color:var(--accent-copper);">${r.day}</div>
                      </td>
                      <td style="font-weight:600; color:var(--text-primary);">${r.department}</td>
                      <td style="font-size:12px; color:var(--text-secondary);">${r.year_section}</td>
                      <td>
                        <span style="font-family:var(--font-mono); font-weight:700; font-size:13px; color:${r.student_count >= 200 ? 'var(--accent-copper)' : 'var(--text-primary)'};">
                          ${r.student_count}
                        </span>
                        <span style="font-size:11px; color:var(--text-secondary);">students</span>
                      </td>
                      <td>
                        <span class="unit-badge" style="font-size:11px; background:${isRush ? 'rgba(201,113,61,0.15)' : 'var(--bg-chalkboard)'}; color:${isRush ? 'var(--accent-copper)' : 'var(--text-primary)'}; border-color:${isRush ? 'var(--accent-copper)' : 'var(--border-subtle)'};">
                          ${r.activity_type}
                        </span>
                      </td>
                      <td style="font-size:12px; color:var(--text-secondary);">${r.location}</td>
                      <td style="font-size:11.5px; color:${isRush ? 'var(--accent-copper)' : 'var(--text-secondary)'};">
                        ${isRush ? `🔥 Canteen Release: ~${Math.round(r.student_count * this.diningFactor)} diners` : 'In Class/Lab'}
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>
        </div>
      ` : ''}
    `;

    if (window.lucide) window.lucide.createIcons();
    this.attachEventListeners();
  }

  attachEventListeners() {
    const dropzone = this.container.querySelector('#tt-csv-dropzone');
    const fileInput = this.container.querySelector('#tt-file-input');
    const browseBtn = this.container.querySelector('#btn-browse-tt-file');
    const loadDemoBtn = this.container.querySelector('#btn-load-demo-tt');
    const dlTemplateBtn = this.container.querySelector('#btn-dl-timetable-template');
    const exportPlanBtn = this.container.querySelector('#btn-export-food-plan');
    const diningSlider = this.container.querySelector('#tt-dining-slider');
    const diningVal = this.container.querySelector('#tt-dining-val');
    const bufferSlider = this.container.querySelector('#tt-buffer-slider');
    const bufferVal = this.container.querySelector('#tt-buffer-val');
    const searchInput = this.container.querySelector('#tt-search-input');

    // Dining attendance slider
    diningSlider?.addEventListener('input', () => {
      this.diningFactor = parseInt(diningSlider.value) / 100.0;
      if (diningVal) diningVal.textContent = `${diningSlider.value}%`;
      this.computeFoodPlan();
      this.render();
    });

    // Buffer slider
    bufferSlider?.addEventListener('input', () => {
      this.safetyBufferPct = parseFloat(bufferSlider.value);
      if (bufferVal) bufferVal.textContent = `+${this.safetyBufferPct}%`;
      this.computeFoodPlan();
      this.render();
    });

    // Browse file
    browseBtn?.addEventListener('click', () => fileInput?.click());

    fileInput?.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        this.readFile(e.target.files[0]);
      }
    });

    // Drag & Drop
    ['dragenter', 'dragover'].forEach(ev => {
      dropzone?.addEventListener(ev, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(ev => {
      dropzone?.addEventListener(ev, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone?.addEventListener('drop', (e) => {
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        this.readFile(e.dataTransfer.files[0]);
      }
    });

    // Load Demo Timetable
    loadDemoBtn?.addEventListener('click', () => {
      this.timetableData = this.parseCSV(generateSampleTimetableCSV());
      this.computeFoodPlan();
      this.render();
    });

    // Download Timetable Template
    dlTemplateBtn?.addEventListener('click', () => {
      const csvStr = generateSampleTimetableCSV();
      const blob = new Blob([csvStr], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'campus_timetable_template.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    });

    // Export Food Plan CSV
    exportPlanBtn?.addEventListener('click', () => {
      this.exportFoodPlanCSV();
    });

    // Day selection buttons
    this.container.querySelectorAll('[data-day]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.selectedDay = btn.getAttribute('data-day');
        this.computeFoodPlan();
        this.render();
      });
    });

    // Search input
    searchInput?.addEventListener('input', (e) => {
      this.searchQuery = e.target.value;
      this.render();
      const newSearch = this.container.querySelector('#tt-search-input');
      if (newSearch) {
        newSearch.focus();
        newSearch.selectionStart = newSearch.selectionEnd = newSearch.value.length;
      }
    });
  }

  readFile(file) {
    if (file.name.toLowerCase().endsWith('.pdf')) {
      const dropzone = this.container.querySelector('#tt-csv-dropzone');
      if (dropzone) dropzone.style.opacity = '0.5';
      
      const formData = new FormData();
      formData.append('file', file);
      
      fetch('/api/timetable/upload-pdf', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (dropzone) dropzone.style.opacity = '1';
        if (!data.success && !data.csv_text) {
          alert('Failed to extract table from PDF: ' + (data.detail || data.message || 'Unknown error'));
          return;
        }
        const parsed = this.parseCSV(data.csv_text);
        if (!parsed.length) {
          alert('Could not parse any rows from the PDF timetable. Please check formatting.');
          return;
        }
        this.timetableData = parsed;
        this.computeFoodPlan();
        this.render();
      })
      .catch(err => {
        if (dropzone) dropzone.style.opacity = '1';
        alert(`Failed to upload PDF: ${err.message}`);
      });
      return;
    }

    if (!file.name.toLowerCase().endsWith('.csv')) {
      alert('Please select a valid .csv or .pdf timetable file.');
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        const parsed = this.parseCSV(text);
        if (!parsed.length) {
          alert('Could not parse any rows from the timetable CSV. Please check formatting.');
          return;
        }
        this.timetableData = parsed;
        this.computeFoodPlan();
        this.render();
      } catch (err) {
        alert(`Failed to read CSV: ${err.message}`);
      }
    };
    reader.readAsText(file);
  }

  exportFoodPlanCSV() {
    if (!this.analyzedPlan) return;
    const p = this.analyzedPlan;

    const rows = [
      ["SERVO AI - TIMETABLE FOOD MANAGEMENT & KITCHEN REQUISITION PLAN"],
      ["Selected Schedule Horizon", this.selectedDay],
      ["Total Scheduled Students", p.totalScheduledStudents],
      ["Dining Attendance Conversion Rate", `${Math.round(this.diningFactor * 100)}%`],
      ["Pantry Safety Buffer Applied", `+${this.safetyBufferPct}%`],
      [],
      ["MEAL SHIFT", "TIME WINDOW", "PROJECTED PORTIONS (COVERS)", "FOOD MENU DESIGN"],
      ["Breakfast Rush", "07:30 - 09:30", p.covers.breakfast, "Idli Sambar, Masala Dosa, Poha, Filter Coffee"],
      ["Staggered Lunch (Batch 1)", "12:00 - 13:00", p.staggeredLunch.batch1_covers, "Veg & Non-Veg South Indian Thalis (Mech & Civil Releases)"],
      ["Staggered Lunch (Batch 2)", "13:00 - 14:00", p.staggeredLunch.batch2_covers, "Dum Biryani, Jeera Rice, Phulkas (CS, EC, Biotech Peak Surge)"],
      ["Evening Snacks & Tea", "16:00 - 18:00", p.covers.snacks, "Hot Samosas, Vada Pav, Veg Cutlet, Cardamom Chai"],
      ["Hostel Dinner", "19:30 - 21:30", p.covers.dinner, "Fresh Phulkas, Paneer Butter Masala / Chicken Curry, Dal Tadka"],
      ["TOTAL DAILY COVERS", "", p.covers.total, ""],
      [],
      ["RAW PANTRY INGREDIENT", "UNIT", "BUFFERED QUANTITY", "CURRENT UNIT PRICE (INR)"],
      ["Premium Sona Masoori Rice", "kg", p.pantry.rice_kg, "58.00"],
      ["Toor & Moong Pulses", "kg", p.pantry.dal_kg, "145.00"],
      ["Fresh Mixed Seasonal Vegetables", "kg", p.pantry.veg_kg, "42.00"],
      ["Full Cream Dairy Milk", "Litres", p.pantry.milk_l, "64.00"],
      ["Refined Sunflower Cooking Oil", "Litres", p.pantry.oil_l, "135.00"],
      ["Whole Wheat Atta (Flour)", "kg", p.pantry.atta_kg, "40.00"],
      ["ESTIMATED GROCERY COST", "INR", p.pantry.est_cost, ""],
      [],
      ["CHEF'S BELL SCHEDULE TIMELINE", "TASK DETAILS", "RELEASE BELL TIMING"],
      ...p.prepTimeline.map(step => [step.time, step.task, step.rushBell])
    ];

    const csvContent = rows.map(r => r.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `timetable_food_management_plan_${this.selectedDay.toLowerCase()}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }
}
