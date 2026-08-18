# Schema.org JSON-LD Examples

Complete, copy-paste ready JSON-LD examples for common schema types. Use with the `<JsonLd>` component and `schema-dts` types.

## Organization (Every Site)

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://example.com/#organization",
  "name": "Your Company Name",
  "url": "https://example.com",
  "logo": {
    "@type": "ImageObject",
    "url": "https://example.com/logo.png",
    "width": 512,
    "height": 512
  },
  "description": "What your company does in one sentence.",
  "sameAs": [
    "https://twitter.com/yourcompany",
    "https://linkedin.com/company/yourcompany",
    "https://github.com/yourcompany"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+1-800-555-0100",
    "contactType": "customer service",
    "availableLanguage": ["English"]
  }
}
```

## WebSite + SearchAction (Every Site)

Enables the sitelinks searchbox in Google for brand queries:

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "url": "https://example.com",
  "name": "Your Site Name",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://example.com/search?q={search_term_string}"
  }
}
```

> **Note**: Google also accepts `target` as an `EntryPoint` object with `urlTemplate` and `query-input`, but `schema-dts` types do not include `query-input`. Use the simplified `target` string format above for type-safe TypeScript, or use a type assertion if you need the full format.

## BreadcrumbList (All Inner Pages)

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Products",
      "item": "https://example.com/products"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Running Shoes",
      "item": "https://example.com/products/running-shoes"
    }
  ]
}
```

## Article / BlogPosting

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Your Article Headline (max 110 chars)",
  "description": "Short summary of the article in 1-2 sentences.",
  "image": "https://example.com/article-hero.jpg",
  "datePublished": "2026-03-15T09:00:00Z",
  "dateModified": "2026-03-20T14:30:00Z",
  "author": {
    "@type": "Person",
    "name": "Jane Smith",
    "url": "https://example.com/authors/jane-smith"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Your Site Name",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/blog/your-article"
  }
}
```

For news articles, change `@type` to `"NewsArticle"`.

## Product + Offer

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Ultra Running Shoes Pro",
  "image": [
    "https://example.com/shoes-front.jpg",
    "https://example.com/shoes-side.jpg"
  ],
  "description": "Lightweight trail running shoes with carbon-fiber plate.",
  "sku": "URS-PRO-001",
  "brand": {
    "@type": "Brand",
    "name": "SpeedRun"
  },
  "offers": {
    "@type": "Offer",
    "price": "149.99",
    "priceCurrency": "USD",
    "priceValidUntil": "2026-12-31",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition",
    "url": "https://example.com/products/ultra-running-shoes-pro",
    "seller": {
      "@type": "Organization",
      "name": "Your Store"
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.7",
    "reviewCount": "256"
  }
}
```

## HowTo (Tutorials, Guides)

Rich result appears on mobile and voice search only (desktop display removed in 2023):

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Deploy a Next.js App to Vercel",
  "description": "Step-by-step guide to deploying your Next.js application.",
  "totalTime": "PT10M",
  "tool": [
    { "@type": "HowToTool", "name": "Vercel CLI" },
    { "@type": "HowToTool", "name": "Git" }
  ],
  "step": [
    {
      "@type": "HowToStep",
      "position": 1,
      "name": "Install Vercel CLI",
      "text": "Run npm i -g vercel to install the Vercel CLI globally.",
      "image": "https://example.com/step1.png"
    },
    {
      "@type": "HowToStep",
      "position": 2,
      "name": "Link your project",
      "text": "Run vercel link in your project directory to connect it to Vercel.",
      "image": "https://example.com/step2.png"
    },
    {
      "@type": "HowToStep",
      "position": 3,
      "name": "Deploy",
      "text": "Run vercel --prod to deploy to production.",
      "image": "https://example.com/step3.png"
    }
  ]
}
```

## Event

Only for genuine, publicly verifiable events:

```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "Annual Tech Summit 2026",
  "description": "Two-day conference covering AI, cloud, and developer tools.",
  "startDate": "2026-06-15T09:00:00+00:00",
  "endDate": "2026-06-16T18:00:00+00:00",
  "eventStatus": "https://schema.org/EventScheduled",
  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
  "location": {
    "@type": "Place",
    "name": "Convention Center",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "500 Convention Blvd",
      "addressLocality": "San Francisco",
      "addressRegion": "CA",
      "addressCountry": "US"
    }
  },
  "organizer": {
    "@type": "Organization",
    "name": "TechEvents Inc.",
    "url": "https://techevents.example.com"
  },
  "offers": {
    "@type": "Offer",
    "price": "299",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "validFrom": "2026-01-01T00:00:00Z",
    "url": "https://techevents.example.com/tickets"
  },
  "image": "https://techevents.example.com/summit-banner.jpg"
}
```

## LocalBusiness

```json
{
  "@context": "https://schema.org",
  "@type": "Restaurant",
  "name": "The Corner Bistro",
  "image": "https://example.com/bistro.jpg",
  "url": "https://cornerbistro.example.com",
  "telephone": "+1-555-0100",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main Street",
    "addressLocality": "Austin",
    "addressRegion": "TX",
    "postalCode": "78701",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 30.2672,
    "longitude": -97.7431
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "11:00",
      "closes": "22:00"
    },
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Saturday", "Sunday"],
      "opens": "10:00",
      "closes": "23:00"
    }
  ],
  "priceRange": "$$",
  "servesCuisine": "American",
  "acceptsReservations": "true"
}
```

## SoftwareApplication

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Your App Name",
  "operatingSystem": "Web",
  "applicationCategory": "DeveloperApplication",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": 1024
  }
}
```

## Implementation Priority

1. **Every site (root layout):** Organization + WebSite + SearchAction
2. **All inner pages:** BreadcrumbList
3. **Blog/news:** Article or NewsArticle
4. **E-commerce:** Product + Offer + AggregateRating
5. **Tutorials:** HowTo (mobile rich result only)
6. **Events:** Event (genuine, verifiable events only)
7. **Local business:** LocalBusiness with geo + hours
8. **Do NOT implement:** FAQPage (restricted to gov/health since 2023)
