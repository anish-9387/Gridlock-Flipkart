# **CascadeIQ**

## **Predicting Event Escalation Before It Becomes Gridlock**

### **Gridlock Hackathon — Event-Driven Congestion Theme**

---

# **Tagline**

**Cities don't fail because of events. They fail because of cascades.**

**CascadeIQ predicts how disruptions spread, how much time authorities have before escalation, and the exact decision window where intervention could have prevented city-wide failure.**

---

# **Executive Summary**

Traffic management systems today are primarily reactive.

Authorities can see:

* What happened  
* Where it happened  
* Current traffic conditions

But they cannot reliably answer:

* Will this event escalate?  
* Which junctions will be affected next?  
* How long until the network reaches a critical state?  
* Which disruptions are preventable?  
* What decision could have stopped the cascade?

CascadeIQ addresses this gap.

Rather than focusing solely on congestion prediction, CascadeIQ focuses on **event escalation prediction**.

The system combines:

* Event intelligence  
* Road network propagation modeling  
* Time-to-Failure estimation  
* Historical replay validation  
* Root-cause analysis  
* Decision-window discovery

to help authorities understand not just what is happening, but how and when a disruption becomes city-wide gridlock.

---

# **Problem**

Traffic authorities manage both:

## **Planned Events**

* Festivals  
* Sports Matches  
* Political Rallies  
* VIP Movement  
* Processions  
* Construction Activities

## **Unplanned Events**

* Accidents  
* Vehicle Breakdowns  
* Waterlogging  
* Tree Falls  
* Sudden Gatherings

These events frequently evolve into severe congestion because of:

* Delayed intervention  
* Poor situational awareness  
* Resource bottlenecks  
* Escalating secondary effects

Most existing systems identify traffic problems only after they have already developed.

---

# **Core Insight**

Most systems think:

Event  
↓  
Congestion

Reality is:

Event  
↓  
Local Disruption  
↓  
Network Stress  
↓  
Junction Overload  
↓  
Spillback  
↓  
Escalation  
↓  
City-Wide Gridlock

The congestion itself is not the problem.

The escalation is.

CascadeIQ is designed to predict and analyze escalation.

---

# **Research Insights**

Research across transportation systems, incident management, disaster response, and infrastructure resilience revealed several recurring findings.

### **Key Finding 1**

Many major traffic failures originate from relatively small incidents.

Examples:

* Vehicle breakdowns  
* Clearance delays  
* Temporary lane blockages

These often trigger cascading failures that become far larger than the original event.

---

### **Key Finding 2**

Traffic failures are frequently operational failures.

Common contributing factors include:

* Delayed dispatch  
* Poor coordination  
* Resource contention  
* Late intervention

---

### **Key Finding 3**

Cities lack institutional memory.

Historical incidents are recorded but rarely transformed into operational intelligence.

As a result, similar failures repeat.

---

### **Key Finding 4**

The most useful metric is not congestion level.

The most useful metric is:

# **Time-To-Failure**

How much time remains before a disruption escalates into a network-wide failure.

This became the foundation of CascadeIQ.

---

# **System Architecture**

CascadeIQ focuses on four tightly scoped and deeply implemented components.

---

# **Component 1 — Event Escalation Engine**

## **Purpose**

Predict whether an event is likely to escalate.

---

## **Inputs**

* Event Type  
* Event Cause  
* Priority  
* Road Closure Requirement  
* Zone  
* Corridor  
* Junction  
* Time Features  
* Historical Event Patterns

---

## **Engineered Features**

Examples:

* Peak Hour Indicator  
* Historical Resolution Time  
* Historical Cascade Rate  
* Concurrent Event Count  
* Corridor Centrality  
* Junction Connectivity

---

## **Outputs**

{  
  "cascade\_probability": 0.81,  
  "predicted\_severity": 2.4,  
  "time\_to\_failure\_minutes": 43,  
  "risk\_level": "High"  
}

---

## **Signature Metric**

### **Time-To-Failure (TTF)**

Instead of:

Risk \= High

CascadeIQ provides:

Time Until Escalation \= 43 Minutes

This becomes the primary operational decision metric.

---

# **Component 2 — Network Propagation Engine**

## **Purpose**

Predict how disruption spreads through the road network.

---

## **Road Graph Construction**

Built using:

* OpenStreetMap  
* OSMnx  
* NetworkX

Each junction becomes a node.

Each road becomes an edge.

---

## **Junction Fragility Score**

Unlike traditional traffic systems that identify busy roads, CascadeIQ identifies fragile roads.

### **Fragility Formula**

Fragility Score \=  
0.4 × Betweenness Centrality  
\+  
0.3 × Historical Cascade Rate  
\+  
0.2 × Junction Degree  
\+  
0.1 × Peak-Hour Incident Frequency

Higher scores indicate locations where small disruptions can create disproportionate network-wide impact.

---

## **Cascade Propagation**

Once escalation begins, the system simulates how stress propagates through connected junctions.

Example:

Junction A  
↓  
Junction B  
↓  
Junction C  
↓  
Corridor D

---

## **Visualization**

Animated propagation map.

Example:

T+0  
Event Starts

T+12  
Junction B At Risk

T+24  
Junction C At Risk

T+43  
Network Critical

This becomes the visual centerpiece of the demo.

---

# **Component 3 — Traffic Black Box**

## **Purpose**

Understand why disruption occurred.

Inspired by aviation-style post-event analysis.

---

## **Event Reconstruction**

Example:

18:05 Event Starts

18:14 Breakdown Reported

18:20 Tow Requested

18:37 Queue Threshold Exceeded

18:48 Diversion Activated

19:05 Gridlock Begins

---

## **Root Cause Analysis**

Outputs:

### **Primary Cause**

Delayed Clearance

### **Contributing Factors**

Peak-Hour Traffic

High Corridor Centrality

Resource Contention

---

## **Avoidable Delay Analysis**

Example:

Actual Resolution:  
182 Minutes

Historical Median:  
95 Minutes

Avoidable Delay:  
87 Minutes

This converts raw traffic data into operational learning.

---

# **Component 4 — Cascade Autopsy ⭐**

## **Purpose**

Identify the exact decision window where escalation was still preventable.

This is the flagship feature of CascadeIQ.

---

## **Core Question**

Most post-event systems answer:

What happened?

Cascade Autopsy answers:

When did we lose the ability to stop it?

---

## **Method**

The system replays a historical event.

Then it runs a counterfactual simulation.

The intervention timing is shifted minute by minute.

A binary search identifies:

### **The Last Successful Intervention Point**

The precise moment where intervention would still have prevented the cascade.

---

## **Output**

Point of No Return:  
18:23

Decision Window:  
4 Minutes

Required Action:  
Tow Dispatch

Cascade Prevented:  
Yes

Delay Saved:  
94 Minutes

Affected Junctions Saved:  
5

---

## **Split Timeline Visualization**

### **Reality**

18:05 Festival Starts

18:14 Breakdown Reported

18:20 Tow Requested

18:26 Dispatch Delayed

18:37 Queue Threshold Crossed

19:05 Gridlock Begins

### **Counterfactual**

18:05 Festival Starts

18:14 Breakdown Reported

18:18 Tow Auto-Flagged

18:21 Dispatch Confirmed

18:29 Tow Arrives

18:31 Queue Cleared

18:48 Normal Flow

---

### **Key Outcome**

Cascade Never Occurs

This provides a powerful visual explanation of preventable failures.

---

# **Historical Replay Mode**

## **Purpose**

Demonstrate that the system works on unseen historical events.

Instead of asking judges to trust predictions, we show:

Historical Event  
↓  
Run Through CascadeIQ  
↓  
Generate Predictions  
↓  
Compare Against Actual Outcome

---

## **Example**

### **Prediction**

Cascade Probability:  
78%

Time-To-Failure:  
46 Minutes

### **Actual Outcome**

Gridlock Occurred:  
49 Minutes Later

This provides validation and credibility.

---

# **Machine Learning Pipeline**

## **Classification Model**

Predicts:

* Escalation Probability

Potential algorithms:

* XGBoost  
* Random Forest

---

## **Regression Model**

Predicts:

* Time-To-Failure

Potential algorithms:

* Gradient Boosting Regressor  
* XGBoost Regressor

---

## **Explainability**

Using SHAP:

* Feature Importance  
* Prediction Drivers  
* Transparent Decision Making

---

# **Validation Strategy**

## **Train/Test Split**

Time-aware split.

Example:

Training:  
January → September

Testing:  
October → December

Avoids temporal leakage.

---

## **Model Card**

Cascade Classifier

AUC-ROC:  
\[To Be Filled After Training\]

Precision:  
\[To Be Filled\]

Recall:  
\[To Be Filled\]

Time-To-Failure Model

MAE:  
\[To Be Filled\]

RMSE:  
\[To Be Filled\]

---

# **Demo Flow**

## **Step 1**

Load historical event.

---

## **Step 2**

Run Event Escalation Engine.

Display:

Cascade Probability:  
81%

Time-To-Failure:  
43 Minutes

---

## **Step 3**

Show animated propagation map.

Display escalation spreading across the road network.

---

## **Step 4**

Reveal actual historical outcome.

Compare prediction vs reality.

---

## **Step 5**

Open Traffic Black Box.

Show:

* Timeline  
* Root Cause  
* Avoidable Delay

---

## **Step 6**

Run Cascade Autopsy.

Reveal:

Point Of No Return:  
18:23

Decision Window:  
4 Minutes

Potential Delay Saved:  
94 Minutes

---

# **Technical Stack**

## **Data**

* Pandas  
* GeoPandas

## **Network Modeling**

* OSMnx  
* NetworkX

## **Machine Learning**

* XGBoost  
* Scikit-Learn

## **Explainability**

* SHAP

## **Visualization**

* Folium  
* Plotly

## **Frontend**

* Streamlit

## **Optional LLM Layer**

Used only for:

* Black Box Narrative Generation  
* Human-readable Incident Reports

No chatbot.

No generic AI assistant.

---

# **Future Extensions**

Not part of MVP.

Potential future directions:

* Resource Optimization  
* Intervention Recommendation Engine  
* Near-Miss Learning  
* Multi-Event Interaction Modeling  
* Operational Playbook Generation

---

# **Why CascadeIQ Is Different**

Most systems answer:

What happened?

Some systems answer:

What will happen?

CascadeIQ answers:

How will disruption spread?

How much time do we have before escalation?

Which junctions will fail next?

Why did the failure occur?

What was the exact moment the city could still have prevented it?

---

# **One-Line Pitch**

**CascadeIQ is a traffic escalation intelligence platform that predicts how event-driven disruptions propagate through urban road networks, estimates Time-To-Failure before gridlock occurs, and identifies the exact decision window where intervention could have prevented the cascade.**

