import { Helmet } from 'react-helmet-async';

function Title({children = "MANAGE"}){
    return(
        <Helmet>
            <meta charSet="utf-8"/>
            <title>{children}</title>
            <meta name="description" content="Default description for the page"/>
        </Helmet>
    )
}

export default Title