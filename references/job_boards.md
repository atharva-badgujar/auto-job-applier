# Job Boards Reference

Search URL patterns and tips for each major job board. Use these to construct
targeted web search queries or direct job search links.

---

## India-Focused Boards

### Naukri.com
- Search URL: `https://www.naukri.com/{role}-jobs-in-{city}`
- Example: `https://www.naukri.com/python-developer-jobs-in-pune`
- Web search query: `site:naukri.com "{role}" "{skill}" jobs Pune`
- Best for: Mid/senior IT roles, large Indian companies

### LinkedIn India
- Search URL: `https://www.linkedin.com/jobs/search/?keywords={role}&location={city}`
- Best for: MNCs, startups, remote roles
- Filter for Easy Apply: add `&f_AL=true`

### Internshala
- Search URL: `https://internshala.com/jobs/{role}-jobs`
- Best for: Internships, entry-level, freshers

### AngelList / Wellfound
- Search URL: `https://wellfound.com/role/l/{role}/{city}`
- Best for: Startups, equity roles

### Instahyre
- Best for: Senior engineers, product managers in India

### Indeed India
- Search URL: `https://in.indeed.com/jobs?q={role}&l={city}`
- Best for: Broad coverage across all levels

---

## Global Boards

### LinkedIn
- Search URL: `https://www.linkedin.com/jobs/search/?keywords={role}&location={location}`
- Best for: International roles, networking

### Indeed
- Search URL: `https://www.indeed.com/jobs?q={role}&l={location}`

### Glassdoor
- Search URL: `https://www.glassdoor.com/Job/{role}-jobs-SRCH_KO0,{len}.htm`
- Best for: Salary info + job listings combined

### RemoteOK
- Search URL: `https://remoteok.com/remote-{role}-jobs`
- Best for: Remote-only roles globally

### We Work Remotely
- URL: `https://weworkremotely.com/categories/remote-programming-jobs`
- Best for: Remote dev jobs

---

## Effective Web Search Queries

Use these query templates with the web_search tool:

```
# General match
"{role}" "{top_skill}" jobs "{location}" 2025

# India-specific
"{role}" jobs Pune OR Mumbai OR Bangalore "{skill}" "apply now"

# Remote
"{role}" remote job "{skill1}" OR "{skill2}" hiring 2025

# Startup-focused
"{role}" startup job India "{skill}" equity

# With experience filter
"2-4 years" "{role}" "{skill}" jobs India

# LinkedIn targeted
site:linkedin.com/jobs "{role}" "{skill}" "{location}"

# Naukri targeted
site:naukri.com "{role}" "{skill}" jobs
```

---

## Application Tracking Status Values (resumex.dev)

| Status | When to use |
|---|---|
| `wishlist` | Found job, not yet applied |
| `applied` | Application submitted |
| `interview` | Got a response / scheduled interview |
| `offer` | Received offer |
| `rejected` | Application rejected / no response after 4 weeks |
